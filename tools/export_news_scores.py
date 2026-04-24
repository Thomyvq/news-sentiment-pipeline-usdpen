import pandas as pd
import sqlite3

DB_PATH = "data/artifacts/pipeline.db"
OUT_CSV = "data/reports/news_scores.csv"

def main():
    con = sqlite3.connect(DB_PATH)
    q = """
    SELECT
      substr(r.fetched_at,1,10) AS day,
      r.source,
      c.title_clean,
      sn.sentiment_label,
      ss.sent_score_std AS score_std,
      ss.sent_strength AS strength,
      r.url
    FROM raw_news r
    JOIN clean_news c ON c.news_id = r.news_id
    JOIN sentiment_news sn ON sn.news_id = r.news_id
    JOIN sentiment_std_news ss ON ss.news_id = r.news_id
    ORDER BY day DESC, score_std ASC;
    """
    df = pd.read_sql_query(q, con)

    # micro-señal por noticia
    thr = 0.15
    df["news_signal"] = "neutral"
    df.loc[df["score_std"] >= thr, "news_signal"] = "up"
    df.loc[df["score_std"] <= -thr, "news_signal"] = "down"

    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print("OK ->", OUT_CSV)

if __name__ == "__main__":
    main()
