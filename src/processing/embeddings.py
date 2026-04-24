import os, json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def _paths(faiss_dir):
    os.makedirs(faiss_dir, exist_ok=True)
    return os.path.join(faiss_dir, "index.faiss"), os.path.join(faiss_dir, "meta.jsonl")

def run_embeddings(db, models_cfg, pipeline_cfg):
    model_name = models_cfg["embeddings"]["hf_model"]
    prefix = models_cfg["embeddings"].get("prefix_passage", "")
    faiss_dir = pipeline_cfg["storage"]["faiss_dir"]
    idx_path, meta_path = _paths(faiss_dir)

    model = SentenceTransformer(model_name)

    rows = db.fetchall("""
        SELECT c.news_id, c.text_clean
        FROM clean_news c
        JOIN lang_news l ON l.news_id = c.news_id
        WHERE l.route != 'manual_review'
          AND c.quality_flags NOT LIKE '%too_short%'
          AND c.news_id NOT IN (SELECT news_id FROM enriched_news)
    """)
    if not rows:
        return

    # init/load index
    test_vec = model.encode([prefix + rows[0]["text_clean"]], normalize_embeddings=True).astype("float32")
    dim = int(test_vec.shape[1])

    if os.path.exists(idx_path):
        index = faiss.read_index(idx_path)
    else:
        index = faiss.IndexFlatIP(dim)

    start_id = index.ntotal

    with open(meta_path, "a", encoding="utf-8") as mf:
        for i, r in enumerate(rows):
            vec = model.encode([prefix + r["text_clean"]], normalize_embeddings=True).astype("float32")
            index.add(vec)
            faiss_id = start_id + i
            mf.write(json.dumps({"faiss_id": faiss_id, "news_id": r["news_id"]}) + "\n")

            db.upsert("enriched_news", {
                "news_id": r["news_id"],
                "faiss_id": faiss_id,
                "embedding_model": model_name,
                "ner_model": "",
                "entities_json": "[]",
                "topic_label": "",
                "topic_score": None,
                "topic_model": ""
            }, key="news_id")

    faiss.write_index(index, idx_path)
