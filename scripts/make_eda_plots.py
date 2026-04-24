from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def main():
    daily_path = Path("data/processed/daily_sentiment.csv")
    scores_path = Path("data/processed/news_scores.csv")  # fallback

    out_dir = Path("figs")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not daily_path.exists():
        raise FileNotFoundError(
            f"No existe {daily_path}. Ejecuta primero el pipeline para generar daily_sentiment.csv"
        )

    df_daily = pd.read_csv(daily_path)

    if "date" not in df_daily.columns:
        raise RuntimeError(f"'date' no existe en {daily_path}. Columnas: {list(df_daily.columns)}")

    # Parse fecha y ordenar
    df_daily["date"] = pd.to_datetime(df_daily["date"], errors="coerce")
    df_daily = df_daily.dropna(subset=["date"]).sort_values("date")

    # === ACOTAR RANGO DE FECHAS ===
    start_date = pd.to_datetime("2025-12-15")
    end_date   = pd.to_datetime("2026-01-09")

    df_daily = df_daily[
        (df_daily["date"] >= start_date) &
        (df_daily["date"] <= end_date)
    ]

    # =========================
    # 1) Barras: noticias por día
    # =========================
    if "n_news_total" in df_daily.columns:
        df_counts = df_daily[["date", "n_news_total"]].copy()
        df_counts["day"] = df_counts["date"].dt.date  # ✅ columna explícita
        df_counts = df_counts.groupby("day", as_index=False)["n_news_total"].sum()

        x = pd.to_datetime(df_counts["day"])
        y = df_counts["n_news_total"]
        title_counts = "Noticias por día (n_news_total)"
    else:
        # Fallback si no existiera n_news_total
        if not scores_path.exists():
            raise RuntimeError("No encuentro n_news_total en daily_sentiment y tampoco existe news_scores.csv.")

        df_scores = pd.read_csv(scores_path)

        date_col = next((c for c in ["date", "published", "published_at", "created_at"] if c in df_scores.columns), None)
        if date_col is None:
            raise RuntimeError(f"No encuentro columna de fecha en news_scores.csv. Columnas: {list(df_scores.columns)}")

        df_scores[date_col] = pd.to_datetime(df_scores[date_col], errors="coerce")
        df_scores = df_scores.dropna(subset=[date_col])
        df_scores["day"] = df_scores[date_col].dt.date

        df_counts = df_scores.groupby("day", as_index=False).size().rename(columns={"size": "n_news_total"})
        x = pd.to_datetime(df_counts["day"])
        y = df_counts["n_news_total"]
        title_counts = "Noticias por día (conteo desde news_scores.csv)"

    plt.figure()
    plt.bar(x, y)
    plt.title(title_counts)
    plt.xlabel("Fecha")
    plt.ylabel("Número de noticias")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out1 = out_dir / "eda_news_per_day.png"
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"OK -> {out1}")

    # =========================
    # 2) Barras: proporción pos/neu/neg en el periodo
    # =========================
    needed = {"share_pos", "share_neu", "share_neg"}

    if needed.issubset(df_daily.columns) and "n_news_total" in df_daily.columns:
        w = df_daily["n_news_total"].fillna(0).clip(lower=0)
        total_w = float(w.sum())
        if total_w == 0:
            raise RuntimeError("n_news_total suma 0, no puedo ponderar proporciones.")

        p_pos = float((df_daily["share_pos"] * w).sum() / total_w)
        p_neu = float((df_daily["share_neu"] * w).sum() / total_w)
        p_neg = float((df_daily["share_neg"] * w).sum() / total_w)

        labels = ["Positive", "Neutral", "Negative"]
        values = [p_pos, p_neu, p_neg]
        title_sent = "Proporción de sentimiento (ponderado por día)"
    else:
        # Fallback usando etiquetas por noticia
        if not scores_path.exists():
            raise RuntimeError("No encuentro shares en daily_sentiment y tampoco existe news_scores.csv.")

        df_scores = pd.read_csv(scores_path)
        label_col = next((c for c in ["sentiment_label", "label"] if c in df_scores.columns), None)
        if label_col is None:
            raise RuntimeError(f"No encuentro columna de etiqueta en news_scores.csv. Columnas: {list(df_scores.columns)}")

        counts = df_scores[label_col].astype(str).str.lower().value_counts()
        pos = int(counts.get("pos", 0) + counts.get("positive", 0))
        neu = int(counts.get("neu", 0) + counts.get("neutral", 0))
        neg = int(counts.get("neg", 0) + counts.get("negative", 0))

        total = pos + neu + neg
        if total == 0:
            raise RuntimeError("No hay etiquetas pos/neu/neg en news_scores.csv.")

        labels = ["Positive", "Neutral", "Negative"]
        values = [pos / total, neu / total, neg / total]
        title_sent = "Proporción de sentimiento (conteo por noticia)"

    plt.figure()
    plt.bar(labels, values)
    plt.title(title_sent)
    plt.ylabel("Proporción")
    plt.ylim(0, 1)
    for i, v in enumerate(values):
        plt.text(i, v, f"{v*100:.1f}%", ha="center", va="bottom")
    plt.tight_layout()
    out2 = out_dir / "eda_sentiment_proportion.png"
    plt.savefig(out2, dpi=200)
    plt.close()
    print(f"OK -> {out2}")


if __name__ == "__main__":
    main()
