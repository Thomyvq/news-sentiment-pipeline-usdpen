def run_signals(db, signals_cfg):
    cfg = signals_cfg["daily"]
    asset = cfg["asset"]
    metric = cfg["metric"]
    thr_pos = float(cfg["threshold_pos"])
    thr_neg = float(cfg["threshold_neg"])
    min_news = int(cfg["min_news"])

    rows = db.fetchall("SELECT * FROM sentiment_timeseries WHERE asset = ? ORDER BY date ASC", [asset])
    for r in rows:
        n = int(r["n_news_total"])
        score = float(r.get(metric) or 0.0)

        if n < min_news:
            label = "neutral"
        else:
            if score >= thr_pos:
                label = "usd_bias_up"
            elif score <= thr_neg:
                label = "usd_bias_down"
            else:
                label = "neutral"

        db.upsert("signals", {
            "date": r["date"],
            "asset": asset,
            "signal_label": label,
            "signal_score": score,
            "rule_version": "v1_thresholds"
        }, key="date")
