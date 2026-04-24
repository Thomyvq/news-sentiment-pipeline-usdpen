# src/pipeline.py

from src.utils.config import load_configs
from src.db.database import DB

from src.ingest.runner import run_ingest
from src.processing.cleaning import run_cleaning
from src.processing.language import run_language
from src.processing.embeddings import run_embeddings
from src.processing.ner import run_ner
from src.processing.topics import run_topics
from src.processing.sentiment import run_sentiment
from src.processing.standardize import run_standardize
from src.processing.aggregate import run_aggregate_daily
from src.signals.rules import run_signals
from src.rag.report import generate_brief
from src.processing.aggregation import aggregate_daily_sentiment
from src.processing.export_daily import export_daily_sentiment

from src.market.fx_yahoo import fetch_usdpen_yahoo
#from src.processing.export_timeseries import export_sentiment_timeseries
from src.eval.compare_signal_vs_fx import compare_daily
from src.eval.table_daily_evaluation import build_daily_evaluation_table

from pathlib import Path
import pandas as pd


def run_all():
    # Cargar configuraciones
    cfg = load_configs()

    # Inicializar base de datos
    db = DB(cfg["pipeline"]["storage"]["sqlite_path"])
    db.init()

    #print("▶ Ingesta de noticias")
    #run_ingest(db, cfg["sources"], cfg["pipeline"])

    print("▶ Ingesta de noticias")
    df_raw = run_ingest(db, cfg["sources"], cfg["pipeline"])  # <- importante: capturar retorno

    # Crear carpeta y guardar SIEMPRE a CSV
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    if df_raw is None:
        raise RuntimeError(
            "La ingesta no retornó un DataFrame (df_raw=None). "
            "Modifica run_ingestion para que retorne el DataFrame o exporta desde DB."
        )

    if not isinstance(df_raw, pd.DataFrame):
        raise TypeError(
            f"La ingesta retornó un tipo inesperado: {type(df_raw)}. "
            "Debe retornar un pandas.DataFrame."
        )

    raw_csv = "data/raw/news_raw.csv"
    df_raw.to_csv(raw_csv, index=False, encoding="utf-8-sig")
    print(f"✔ Guardado RAW: {raw_csv} ({len(df_raw)} filas)")

    print("▶ Limpieza de texto")
    #run_cleaning(db, cfg["pipeline"])
    run_cleaning(None, cfg["pipeline"])

    print("▶ Detección de idioma")
    run_language(db, cfg["pipeline"])

    print("▶ Embeddings + FAISS")
    run_embeddings(db, cfg["models"], cfg["pipeline"])

    print("▶ NER (entidades)")
    run_ner(db, cfg["models"])

    print("▶ Clasificación por tópicos")
    run_topics(db, cfg["models"])

    print("▶ Análisis de sentimiento")
    run_sentiment(db, cfg["models"])

    print("▶ Estandarización de scores")
    run_standardize(db)

    print("▶ Agregación diaria")
    asset = cfg["signals"]["daily"]["asset"]
    run_aggregate_daily(db, asset=asset)

    
    export_daily_sentiment(db)

    start_date = cfg["pipeline"]["date_range"]["start"] if "date_range" in cfg["pipeline"] else "2025-12-01"
    end_date = cfg["pipeline"]["date_range"]["end"] if "date_range" in cfg["pipeline"] else "2026-01-09"

    fx_df = fetch_usdpen_yahoo(start_date, end_date)
    #sent_df = export_sentiment_timeseries(db)

    compare_daily(
        sentiment_csv="data/processed/daily_sentiment.csv",
        fx_csv="data/market/usdpen_yahoo.csv",
        out_path="data/processed/compare_sentiment_vs_fx.csv",
        neutral_band=0.0
    )

    build_daily_evaluation_table(
        sentiment_csv="data/processed/daily_sentiment.csv",
        fx_csv="data/market/usdpen_yahoo.csv",
        out_path="data/processed/daily_evaluation_table.csv",
        neutral_band=0.05
    )

    print("▶ Generación de señales")
    run_signals(db, cfg["signals"])

    print("▶ Generación de brief (RAG)")
    dates = db.fetchall("""
        SELECT date
        FROM sentiment_timeseries
        ORDER BY date ASC
    """)

    for d in dates:
        date_str = d["date"]
        out = generate_brief(
            db,
            cfg["models"],
            cfg["pipeline"],
            date_str,
            asset,
            k=12
        )
        if out:
            print(f"✔ Brief generado: {out}")

    print("\n✅ Pipeline ejecutado correctamente")


if __name__ == "__main__":
    run_all()
