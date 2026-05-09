from transformers import pipeline
from pathlib import Path
import pandas as pd


def _map_label(lbl: str) -> str:
    m = {
        "positive": "pos", "negative": "neg", "neutral": "neu",
        "POSITIVE": "pos", "NEGATIVE": "neg", "NEUTRAL": "neu",
        "pos": "pos", "neg": "neg", "neu": "neu"
    }
    return m.get(lbl, lbl.lower())


def run_sentiment(db, models_cfg):
    en_model = models_cfg["sentiment"]["en"]["hf_model"]
    es_model = models_cfg["sentiment"]["es"]["hf_model"]

    # ✅ Sin deprecated warning + truncado seguro
    pipe_en = pipeline(
        "text-classification",
        model=en_model,
        truncation=True,
        max_length=128,
        top_k=None
    )
    pipe_es = pipeline(
        "text-classification",
        model=es_model,
        truncation=True,
        max_length=128,
        top_k=None
    )

   # rows = db.fetchall("""
    #    SELECT c.news_id, c.text_clean, l.language
    #    FROM clean_news c
    #    JOIN lang_news l ON l.news_id = c.news_id
    #    WHERE l.route != 'manual_review'
    #      AND c.quality_flags NOT LIKE '%too_short%'
    #      AND c.news_id NOT IN (SELECT news_id FROM sentiment_news)
    #""")

####################
    df_clean = pd.read_csv("data/processed/news_clean.csv")

    start_date = models_cfg.get("date_range", {}).get("start", None)
    end_date = models_cfg.get("date_range", {}).get("end", None)

    # Detectar columna de texto válida
    if "body_raw" in df_clean.columns:
        text_col = "body_raw"
    elif "title_raw" in df_clean.columns:
        text_col = "title_raw"
    else:
        raise KeyError(
            f"No se encontró columna de texto. "
            f"Columnas disponibles: {df_clean.columns.tolist()}"
        )

    # Detectar idioma
    if "lang_hint" in df_clean.columns:
        lang_col = "lang_hint"
    else:
        df_clean["language"] = "es"
        lang_col = "language"

    # Eliminar vacíos
    df_clean = df_clean.dropna(subset=[text_col])

    # Convertir a lista de registros
    rows = df_clean[["news_id", text_col, lang_col]].rename(
        columns={
            text_col: "text_clean",
            lang_col: "language"
        }
    ).to_dict("records")

####################

    records_for_csv = []

    for r in rows:
        text = (r["text_clean"] or "")[:4000]
        lang = r["language"]

        try:
            scores = pipe_en(text)[0] if lang == "en" else pipe_es(text)[0]
            model_name = en_model if lang == "en" else es_model
        except Exception:
            continue

        p = {"pos": 0.0, "neu": 0.0, "neg": 0.0}
        for s in scores:
            lab = _map_label(s.get("label", ""))
            if lab in p:
                p[lab] = float(s.get("score", 0.0))

        label = max(p.items(), key=lambda kv: kv[1])[0]

        # ✅ Lo que se guarda en DB (sin 'language' para evitar el error de SQLite)
        rec_db = {
            "news_id": r["news_id"],
            "sentiment_model": model_name,
            "sentiment_label": label,
            "p_pos": p["pos"],
            "p_neu": p["neu"],
            "p_neg": p["neg"],
        }
        try:
            db.upsert("sentiment_news", rec_db, key="news_id")
        except Exception:
            pass

        # (Opcional) lo que exportas a CSV sí puede incluir language
        records_for_csv.append({**rec_db, "language": lang})

    # ✅ Export opcional (sirve para debug / auditoría)

    #rows_all = db.fetchall("""
    #    SELECT news_id, sentiment_model, sentiment_label, p_pos, p_neu, p_neg
    #    FROM sentiment_news
    #""")
    #df_scores = pd.DataFrame(rows_all)
    #df_scores.to_csv("data/processed/news_scores.csv", index=False, encoding="utf-8-sig")

    #print(f"✔ Guardado SCORES: data/processed/news_scores.csv ({len(df_scores)} filas)")

#######################
    df_scores = pd.DataFrame(records_for_csv)

    out_path = Path("data/processed/news_scores.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df_scores.to_csv(
        out_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"✔ Guardado SCORES: {out_path} ({len(df_scores)} filas)")
#######################


    #df_scores = pd.DataFrame(records_for_csv)
    #out_path = Path("data/processed/news_scores.csv")
    #out_path.parent.mkdir(parents=True, exist_ok=True)
    #df_scores.to_csv(out_path, index=False, encoding="utf-8-sig")
    #print(f"✔ Guardado SCORES: {out_path} ({len(df_scores)} filas)")

    return df_scores
