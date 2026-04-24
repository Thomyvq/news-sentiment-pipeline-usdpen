def run_standardize(db):
    rows = db.fetchall("""
        SELECT * FROM sentiment_news
        WHERE news_id NOT IN (SELECT news_id FROM sentiment_std_news)
    """)
    for r in rows:
        p_pos = float(r["p_pos"])
        p_neu = float(r["p_neu"])
        p_neg = float(r["p_neg"])

        score = p_pos - p_neg
        conf = max(p_pos, p_neu, p_neg)
        strength = score * conf

        db.upsert("sentiment_std_news", {
            "news_id": r["news_id"],
            "sent_score_std": score,
            "sent_conf_std": conf,
            "sent_strength": strength,
            "std_method_version": "v1_p_pos_minus_p_neg"
        }, key="news_id")
