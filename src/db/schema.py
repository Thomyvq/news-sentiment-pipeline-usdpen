SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS raw_news (
  news_id TEXT PRIMARY KEY,
  source TEXT,
  url TEXT UNIQUE,
  published_at TEXT,
  fetched_at TEXT,
  title_raw TEXT,
  body_raw TEXT,
  content_hash TEXT,
  lang_hint TEXT,
  reliability_weight REAL
);

CREATE TABLE IF NOT EXISTS clean_news (
  news_id TEXT PRIMARY KEY,
  title_clean TEXT,
  body_clean TEXT,
  text_clean TEXT,
  cleaning_version TEXT,
  quality_flags TEXT,
  length_chars INTEGER
);

CREATE TABLE IF NOT EXISTS lang_news (
  news_id TEXT PRIMARY KEY,
  language TEXT,
  lang_confidence REAL,
  route TEXT
);

CREATE TABLE IF NOT EXISTS enriched_news (
  news_id TEXT PRIMARY KEY,
  faiss_id INTEGER,
  embedding_model TEXT,
  ner_model TEXT,
  entities_json TEXT,
  topic_label TEXT,
  topic_score REAL,
  topic_model TEXT
);

CREATE TABLE IF NOT EXISTS sentiment_news (
  news_id TEXT PRIMARY KEY,
  sentiment_model TEXT,
  sentiment_label TEXT,
  p_pos REAL,
  p_neu REAL,
  p_neg REAL
);

CREATE TABLE IF NOT EXISTS sentiment_std_news (
  news_id TEXT PRIMARY KEY,
  sent_score_std REAL,
  sent_conf_std REAL,
  sent_strength REAL,
  std_method_version TEXT
);

CREATE TABLE IF NOT EXISTS sentiment_timeseries (
  date TEXT PRIMARY KEY,
  asset TEXT,
  n_news_total INTEGER,
  sent_index_mean REAL,
  sent_index_strength REAL,
  share_pos REAL,
  share_neg REAL,
  share_neu REAL
);

CREATE TABLE IF NOT EXISTS signals (
  date TEXT PRIMARY KEY,
  asset TEXT,
  signal_label TEXT,
  signal_score REAL,
  rule_version TEXT
);
"""
