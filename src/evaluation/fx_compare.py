# src/evaluation/fx_compare.py
import pandas as pd

def compare_sentiment_vs_fx(sentiment_path, fx_path, output_path):
    sent = pd.read_csv(sentiment_path, parse_dates=["date"])
    fx = pd.read_csv(fx_path, parse_dates=["date"])

    df = sent.merge(fx, on="date", how="inner")

    df["real_move"] = df.apply(
        lambda r: "Up" if r["close"] > r["open"]
        else "Down" if r["close"] < r["open"]
        else "Flat",
        axis=1
    )

    df["match"] = df["signal"].str.lower() == df["real_move"].str.lower()

    df.to_csv(output_path, index=False)
    return df
