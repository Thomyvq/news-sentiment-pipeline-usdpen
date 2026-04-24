import json
from transformers import pipeline

def run_ner(db, models_cfg):
    ner_en_name = models_cfg["ner"]["en"]["hf_model"]
    ner_es_name = models_cfg["ner"]["es"]["hf_model"]

    ner_en = pipeline("token-classification", model=ner_en_name, aggregation_strategy="simple")
    ner_es = pipeline("token-classification", model=ner_es_name, aggregation_strategy="simple")

    rows = db.fetchall("""
        SELECT c.news_id, c.text_clean, l.language
        FROM clean_news c
        JOIN lang_news l ON l.news_id = c.news_id
        JOIN enriched_news e ON e.news_id = c.news_id
        WHERE l.route != 'manual_review'
    """)

    for r in rows:
        # skip if already have entities
        cur = db.fetchall("SELECT entities_json FROM enriched_news WHERE news_id=?", [r["news_id"]])
        if cur and cur[0].get("entities_json") not in ("[]", "", None):
            continue

        text = (r["text_clean"] or "")[:3500]
        lang = r["language"]

        try:
            ents = ner_en(text) if lang == "en" else ner_es(text)
            model_name = ner_en_name if lang == "en" else ner_es_name
        except Exception:
            continue

        compact = []
        for e in ents:
            compact.append({
                "text": (e.get("word") or "").strip(),
                "type": e.get("entity_group") or e.get("entity") or "",
                "score": float(e.get("score", 0.0)),
                "start": int(e.get("start", -1)),
                "end": int(e.get("end", -1)),
            })

        base = db.fetchall("SELECT * FROM enriched_news WHERE news_id=?", [r["news_id"]])[0]
        base["ner_model"] = model_name
        base["entities_json"] = json.dumps(compact, ensure_ascii=False)
        db.upsert("enriched_news", base, key="news_id")
