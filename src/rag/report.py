import os, json
import faiss
from collections import Counter
from sentence_transformers import SentenceTransformer

def _paths(faiss_dir):
    return os.path.join(faiss_dir, "index.faiss"), os.path.join(faiss_dir, "meta.jsonl")

def _load_meta(meta_path):
    m = {}
    if not os.path.exists(meta_path):
        return m
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                m[int(obj["faiss_id"])] = obj["news_id"]
            except Exception:
                continue
    return m

def _top_entities(db, news_ids, topn=8):
    ents = []
    for nid in news_ids:
        row = db.fetchall("SELECT entities_json FROM enriched_news WHERE news_id=?", [nid])
        if not row: 
            continue
        try:
            arr = json.loads(row[0].get("entities_json") or "[]")
            for e in arr:
                t = (e.get("text") or "").replace("▁", "").strip()
                if len(t) >= 3:
                    ents.append(t)
        except Exception:
            pass
    return [x for x,_ in Counter(ents).most_common(topn)]

def generate_brief(db, models_cfg, pipeline_cfg, date_str: str, asset: str, k=12):
    faiss_dir = pipeline_cfg["storage"]["faiss_dir"]
    idx_path, meta_path = _paths(faiss_dir)
    if not os.path.exists(idx_path):
        return None

    sig = db.fetchall("SELECT * FROM signals WHERE date=? AND asset=?", [date_str, asset])
    if not sig:
        return None
    sig = sig[0]

    # take all news that have embeddings (enriched)
    day_news = db.fetchall("""
      SELECT r.news_id, r.source, r.url, c.title_clean, c.body_clean,
             sn.sentiment_label, ss.sent_score_std,
             e.topic_label
      FROM raw_news r
      JOIN clean_news c ON c.news_id=r.news_id
      JOIN enriched_news e ON e.news_id=r.news_id
      JOIN sentiment_news sn ON sn.news_id=r.news_id
      JOIN sentiment_std_news ss ON ss.news_id=r.news_id
      WHERE substr(r.fetched_at,1,10)=?
    """, [date_str])

    day_ids = [x["news_id"] for x in day_news]
    ents = _top_entities(db, day_ids, topn=6)

    topics = [x["topic_label"] for x in day_news if x.get("topic_label")]
    top_topics = [x for x,_ in Counter(topics).most_common(3)]

    query = f"{asset} drivers {sig['signal_label']} " + " ".join(top_topics + ents)

    emb_model_name = models_cfg["embeddings"]["hf_model"]
    qprefix = models_cfg["embeddings"].get("prefix_query", "")
    model = SentenceTransformer(emb_model_name)

    qvec = model.encode([qprefix + query], normalize_embeddings=True).astype("float32")

    index = faiss.read_index(idx_path)
    meta = _load_meta(meta_path)

    D, I = index.search(qvec, k)
    faiss_ids = [int(i) for i in I[0] if int(i) >= 0]
    news_ids = [meta.get(fid) for fid in faiss_ids if fid in meta]
    news_ids = [nid for nid in news_ids if nid]

    # build output using DB info
    recs = []
    for nid in news_ids:
        row = db.fetchall("""
          SELECT r.source, r.url, c.title_clean, c.body_clean,
                 sn.sentiment_label, ss.sent_score_std,
                 e.topic_label
          FROM raw_news r
          JOIN clean_news c ON c.news_id=r.news_id
          JOIN sentiment_news sn ON sn.news_id=r.news_id
          JOIN sentiment_std_news ss ON ss.news_id=r.news_id
          JOIN enriched_news e ON e.news_id=r.news_id
          WHERE r.news_id=?
        """, [nid])
        if row:
            recs.append(row[0])

    os.makedirs("data/reports", exist_ok=True)
    out_path = f"data/reports/brief_{date_str}.md"

    def short(body):
        parts = [p.strip() for p in (body or "").split(".") if p.strip()]
        return ". ".join(parts[:2]) + ("." if parts else "")

    lines = []
    lines += [f"# Brief Tesorería — {date_str}", ""]
    lines += [f"**Activo:** {asset}", f"**Señal:** `{sig['signal_label']}` | **Score:** `{float(sig['signal_score']):+.3f}`", ""]
    lines += [f"**Query RAG:** `{query}`", ""]
    lines += ["## Noticias clave (Top-K)", ""]

    for i, r in enumerate(recs[:10], start=1):
        lines += [f"### {i}. {r['title_clean']}",
                  f"- Fuente: {r['source']}",
                  f"- Sentimiento: **{r['sentiment_label']}** | score_std={float(r['sent_score_std']):+.3f}",
                  f"- Tópico: `{r.get('topic_label') or ''}`",
                  f"- URL: {r.get('url') or ''}",
                  f"- Resumen: {short(r.get('body_clean'))}",
                  ""]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
