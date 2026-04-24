# src/processing/aggregation.py

from pathlib import Path
import pandas as pd


def aggregate_daily_sentiment(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Lee news_scores (csv o parquet), agrega por día y guarda un daily_agg.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Asegura carpeta de salida
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            f"No existe el archivo de entrada para agregación diaria: {input_path}\n"
            f"✅ Verifica que la etapa de scoring exporte 'news_scores.csv' (o cambia input_path)\n"
            f"✅ Revisa también si se generó como .parquet en la misma carpeta."
        )

    # Leer CSV o Parquet
    if input_path.suffix.lower() == ".csv":
        df = pd.read_csv(input_path, parse_dates=["date"])
    elif input_path.suffix.lower() in [".parquet", ".pq"]:
        df = pd.read_parquet(input_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
    else:
        raise ValueError(f"Formato no soportado: {input_path.suffix}. Usa .csv o .parquet")

    # Validaciones mínimas
    if "date" not in df.columns:
        raise ValueError("El archivo de scores no tiene columna 'date'.")
    if "score" not in df.columns:
        # a veces le ponen sentiment_score, compound, etc.
        possible = [c for c in df.columns if "score" in c.lower()]
        raise ValueError(f"No encuentro columna 'score'. Candidatas: {possible}")

    # Agregación diaria
    daily = (
        df.groupby(df["date"].dt.date, as_index=False)["score"]
        .mean()
        .rename(columns={"date": "day", "score": "score_mean"})
    )

    # Guardar
    if output_path.suffix.lower() == ".csv":
        daily.to_csv(output_path, index=False)
    else:
        # default a csv si no pusieron extensión
        daily.to_csv(str(output_path) if output_path.suffix else str(output_path) + ".csv", index=False)

    return daily
