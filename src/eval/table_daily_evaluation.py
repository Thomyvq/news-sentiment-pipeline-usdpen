import pandas as pd
from pathlib import Path

def build_daily_evaluation_table(
    sentiment_csv="data/processed/daily_sentiment.csv",
    fx_csv="data/market/usdpen_yahoo.csv",
    out_path="data/processed/daily_evaluation_table.csv",
    neutral_band=0.05
):
    s = pd.read_csv(sentiment_csv)
    f = pd.read_csv(fx_csv)

    s["date"] = pd.to_datetime(s["date"]).dt.date
    f["date"] = pd.to_datetime(f["date"]).dt.date

    # Merge por fecha
    df = pd.merge(
        s,
        f[["date", "open", "close"]],
        on="date",
        how="inner"
    )

    # Señal de sentimiento
    def sentiment_signal(x):
        if x > neutral_band:
            return "Positive"
        if x < -neutral_band:
            return "Negative"
        return "Neutral"

    df["Señal Sentimiento"] = df["sent_index_mean"].apply(sentiment_signal)

    # Movimiento real
    def real_movement(o, c):
        if c > o:
            return "Up"
        if c < o:
            return "Down"
        return "Flat"

    df["Movimiento Real"] = df.apply(
        lambda r: real_movement(r["open"], r["close"]), axis=1
    )

    # Coincidencia
    df["Coincide"] = (
        ((df["Señal Sentimiento"] == "Positive") & (df["Movimiento Real"] == "Up")) |
        ((df["Señal Sentimiento"] == "Negative") & (df["Movimiento Real"] == "Down"))
    ).map({True: "✔", False: "✘"})

    # Selección final de columnas (orden tesis)
    table = df[[
        "date",
        "Señal Sentimiento",
        "open",
        "close",
        "Movimiento Real",
        "Coincide"
    ]].rename(columns={
        "date": "Fecha",
        "open": "Apertura",
        "close": "Cierre"
    })

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"✔ Tabla diaria generada: {out_path} ({len(table)} filas)")
    return table
