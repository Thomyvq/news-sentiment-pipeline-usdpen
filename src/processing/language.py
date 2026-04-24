from langdetect import detect_langs

def run_language(db, pipeline_cfg):
    rows = db.fetchall("""
        SELECT * FROM clean_news
        WHERE news_id NOT IN (SELECT news_id FROM lang_news)
    """)
    allowed = set(pipeline_cfg["language"]["allowed"])
    min_conf = float(pipeline_cfg["language"]["min_conf"])

    for r in rows:
        text = (r["text_clean"] or "")[:2000]
        lang, conf = "other", 0.0
        try:
            preds = detect_langs(text)
            if preds:
                top = preds[0]
                lang, conf = top.lang, float(top.prob)
        except Exception:
            pass

        route = "manual_review"
        if lang in allowed and conf >= min_conf:
            route = f"sent_{lang}"

        db.upsert("lang_news", {
            "news_id": r["news_id"],
            "language": lang,
            "lang_confidence": conf,
            "route": route
        }, key="news_id")
