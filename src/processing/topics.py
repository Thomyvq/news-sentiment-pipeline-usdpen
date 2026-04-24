from transformers import pipeline

def run_topics(db, models_cfg):
    tcfg = models_cfg.get("topics", {})
    if not tcfg.get("enabled", False):
        return
    model_name = tcfg["hf_model"]
    labels = tcfg["labels"]

    clf = pipeline("zero-shot-classification", model=model_name)

    rows = db.fetchall("""
        SELECT c.news_id, c.text_clean
        FROM clean_news c
        JOIN lang_news l ON l.news_id = c.news_id
        JOIN enriched_news e ON e.news_id = c.news_id
        WHERE l.route != 'manual_review'
    """)

    for r in rows:
        cur = db.fetchall("SELECT topic_label FROM enriched_news WHERE news_id=?", [r["news_id"]])
        if cur and cur[0].get("topic_label"):
            continue

        text = (r["text_clean"] or "")[:1200]
        try:
            out = clf(text, candidate_labels=labels, multi_label=False)
            label = out["labels"][0]
            score = float(out["scores"][0])
        except Exception:
            continue

        base = db.fetchall("SELECT * FROM enriched_news WHERE news_id=?", [r["news_id"]])[0]
        base["topic_label"] = label
        base["topic_score"] = score
        base["topic_model"] = model_name
        db.upsert("enriched_news", base, key="news_id")
