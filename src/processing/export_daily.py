from pathlib import Path
import pandas as pd

def export_daily_sentiment(db, out_path="data/processed/daily_sentiment.csv") -> pd.DataFrame:
    rows = db.fetchall("""
        SELECT
            date,
            asset,
            n_news_total,
            sent_index_mean,
            sent_index_strength,
            share_pos,
            share_neg,
            share_neu
        FROM sentiment_timeseries
        ORDER BY date ASC
    """)

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("sentiment_timeseries está vacío. Revisa run_aggregate_daily().")

    df["date"] = pd.to_datetime(df["date"]).dt.date

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✔ Exportado: {out_path} ({len(df)} filas)")

    return df
