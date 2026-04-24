from datetime import datetime
from dateutil import parser as dtparser

def _to_date(s: str):
    if not s:
        return None
    try:
        return dtparser.parse(s).date().isoformat()
    except Exception:
        return None

def run_aggregate_daily(db, asset="USD/PEN"):
    rows = db.fetchall("""
        SELECT r.published_at, r.fetched_at, ss.sent_score_std, ss.sent_strength, sn.sentiment_label
        FROM raw_news r
        JOIN sentiment_std_news ss ON ss.news_id = r.news_id
        JOIN sentiment_news sn ON sn.news_id = r.news_id
    """)

    bucket = {}
    for r in rows:
        d = _to_date(r["published_at"]) or _to_date(r["fetched_at"]) or datetime.now().date().isoformat()
        bucket.setdefault(d, {"scores": [], "strengths": [], "labels": []})
        bucket[d]["scores"].append(float(r["sent_score_std"]))
        bucket[d]["strengths"].append(float(r["sent_strength"]))
        bucket[d]["labels"].append(r["sentiment_label"])

    for d, v in bucket.items():
        n = len(v["scores"])
        if n == 0:
            continue

        mean_score = sum(v["scores"]) / n
        mean_strength = sum(v["strengths"]) / n

        pos = sum(1 for lab in v["labels"] if lab == "pos") / n
        neg = sum(1 for lab in v["labels"] if lab == "neg") / n
        neu = sum(1 for lab in v["labels"] if lab == "neu") / n

        db.upsert("sentiment_timeseries", {
            "date": d,
            "asset": asset,
            "n_news_total": n,
            "sent_index_mean": mean_score,
            "sent_index_strength": mean_strength,
            "share_pos": pos,
            "share_neg": neg,
            "share_neu": neu
        }, key="date")
