from pathlib import Path
import pandas as pd

def _fx_direction(open_, close_, eps=0.0):
    if close_ > open_ + eps:
        return "UP"
    if close_ < open_ - eps:
        return "DOWN"
    return "FLAT"

def _sent_to_signal(sent_index_mean, neutral_band=0.0):
    # neutral_band: si quieres considerar neutro cuando |sent_index_mean| < banda
    if sent_index_mean > neutral_band:
        return "UP"
    if sent_index_mean < -neutral_band:
        return "DOWN"
    return "FLAT"

def compare_daily(
    sentiment_csv: str,
    fx_csv: str,
    out_path="data/processed/compare_sentiment_vs_fx.csv",
    neutral_band=0.0
):
    s = pd.read_csv(sentiment_csv)
    f = pd.read_csv(fx_csv)

    s["date"] = pd.to_datetime(s["date"]).dt.date
    f["date"] = pd.to_datetime(f["date"]).dt.date

    # Nos quedamos con open/close
    f = f[["date", "open", "close"]].copy()

    # Merge por fecha
    df = pd.merge(s, f, on="date", how="inner")
    if df.empty:
        raise RuntimeError("El merge quedó vacío. Revisa que las fechas coincidan en ambos CSV.")

    # Validar columna esperada del sentimiento diario
    if "sent_index_mean" not in df.columns:
        raise RuntimeError(
            "No encuentro 'sent_index_mean' en el CSV de sentimiento diario.\n"
            f"Columnas disponibles: {list(df.columns)}"
        )

    # Direcciones
    df["signal"] = df["sent_index_mean"].apply(
        lambda x: _sent_to_signal(float(x), neutral_band=neutral_band)
    )
    df["real_dir"] = df.apply(lambda r: _fx_direction(float(r["open"]), float(r["close"])), axis=1)

    # Acierto simple
    df["hit"] = (df["signal"] == df["real_dir"]).astype(int)

    # Guardar tabla día a día
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✔ Comparación guardada: {out_path} ({len(df)} filas)")

    # Resúmenes
    accuracy = df["hit"].mean() if len(df) else 0.0
    summary = (
        df.groupby(["signal", "real_dir"])["hit"]
          .count()
          .reset_index()
          .rename(columns={"hit": "count"})
    )

    print("\n=== RESUMEN RÁPIDO ===")
    print(f"Filas comparadas: {len(df)}")
    print(f"Accuracy (hit-rate): {accuracy:.3f}")

    print("\nMatriz simple (signal vs real_dir):")
    print(summary.to_string(index=False))

    return df, summary
