# src/processing/cleaning.py
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Optional best mojibake fix
try:
    import ftfy  # type: ignore
except Exception:
    ftfy = None

# Optional HTML parsing
try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None


# -----------------------------
# Regex / constants
# -----------------------------
_CTRL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2060\uFEFF]")
_WS_RE = re.compile(r"[ \t\r\f\v\u00A0]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")

_MOJIBAKE_HINT_RE = re.compile(r"(Ã.|Â.|â€™|â€œ|â€�|â€“|â€”|â€¦|â€|Ð|Þ|�)")

# FIXED regex (your previous error was here)
_BRACKET_NOISE_RE = re.compile(r"\s*\[\s*(?:Reuters|Bloomberg|AP|AFP)\s*\]\s*$", re.IGNORECASE)

_PUNCT_MAP = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201C": '"',
    "\u201D": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00B4": "'",
}

_SEP_MAP = {
    "\u2009": " ",
    "\u202F": " ",
    "\u2063": " ",
}


# -----------------------------
# Low-level helpers
# -----------------------------
def _to_str(x: Any) -> str:
    if x is None:
        return ""
    return x if isinstance(x, str) else str(x)


def decode_html_entities(text: str) -> str:
    text = html.unescape(text)
    text = html.unescape(text)
    return text


def strip_html(text: str) -> str:
    if not text:
        return text
    if BeautifulSoup is not None:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(" ", strip=True)
    return re.sub(r"<[^>]+>", " ", text)


def normalize_unicode(text: str) -> str:
    for k, v in _SEP_MAP.items():
        if k in text:
            text = text.replace(k, v)

    text = unicodedata.normalize("NFC", text)

    for k, v in _PUNCT_MAP.items():
        if k in text:
            text = text.replace(k, v)

    return text


def remove_invisible_and_controls(text: str, keep_newlines: bool = False) -> str:
    if not text:
        return text
    text = _ZERO_WIDTH_RE.sub("", text)
    text = _CTRL_CHARS_RE.sub("", text)
    if not keep_newlines:
        text = text.replace("\n", " ")
    return text


def fix_mojibake(text: str) -> str:
    if not text:
        return text

    if ftfy is not None:
        return ftfy.fix_text(text)

    if not _MOJIBAKE_HINT_RE.search(text):
        return text

    # latin1 -> utf8 attempt (PerÃº -> Perú)
    try:
        repaired = text.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
        if (_MOJIBAKE_HINT_RE.search(repaired) is None) or (repaired.count("�") < text.count("�")):
            return repaired
    except Exception:
        pass

    # cp1252 -> utf8 attempt (â€™)
    try:
        repaired = text.encode("cp1252", errors="ignore").decode("utf-8", errors="ignore")
        if (_MOJIBAKE_HINT_RE.search(repaired) is None) or (repaired.count("�") < text.count("�")):
            return repaired
    except Exception:
        pass

    return text


def normalize_whitespace(text: str) -> str:
    if not text:
        return text
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub(" ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


def clean_text(
    text: Any,
    *,
    strip_tags: bool = True,
    fix_encoding: bool = True,
    keep_newlines: bool = False,
) -> str:
    s = _to_str(text)
    if not s:
        return ""
    s = decode_html_entities(s)
    if strip_tags and ("<" in s and ">" in s):
        s = strip_html(s)
    if fix_encoding:
        s = fix_mojibake(s)
    s = normalize_unicode(s)
    s = remove_invisible_and_controls(s, keep_newlines=keep_newlines)
    s = normalize_whitespace(s)
    return s


def clean_source(source: Any) -> str:
    s = clean_text(source, strip_tags=True, fix_encoding=True, keep_newlines=False)
    s = _BRACKET_NOISE_RE.sub("", s).strip()
    s = re.sub(r"^https?://(www\.)?", "", s, flags=re.IGNORECASE).strip()
    return s


def make_title_clean(title: Any) -> str:
    t = clean_text(title, strip_tags=True, fix_encoding=True, keep_newlines=False)
    t = t.strip('"\'')

    t = re.sub(r"([!?.,:;])\1{1,}", r"\1", t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    t = re.sub(r"([(])\s+", r"\1", t)
    t = re.sub(r"\s+([)])", r"\1", t)

    return t.strip()


# -----------------------------
# High-level pipeline step
# -----------------------------
def run_cleaning(
    db: Optional[Any] = None,
    cfg: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Pipeline step: read raw news, clean text fields, and write processed output.

    Supports:
    - CSV mode (default): reads data/raw/news_raw.csv and writes data/processed/news_clean.csv
    - DB mode (optional): if `db` provides read/write methods, use them.

    Returns cleaned DataFrame.
    """
    cfg = cfg or {}
    io_cfg = cfg.get("io", {})

    input_csv = io_cfg.get("raw_news_csv", "data/raw/news_raw.csv")
    output_csv = io_cfg.get("clean_news_csv", "data/processed/news_clean.csv")

    Path("data/processed").mkdir(parents=True, exist_ok=True)

    # --- Read
    df: pd.DataFrame
    if db is not None:
        # Try common DB helper conventions
        if hasattr(db, "read_table"):
            df = db.read_table("news_raw")
        elif hasattr(db, "read_df"):
            df = db.read_df("news_raw")
        else:
            raise TypeError(
                "db fue provisto pero no tiene métodos read_table/read_df. "
                "Usa CSV mode o adapta tu clase DB."
            )
    else:
        if not Path(input_csv).exists():
            raise FileNotFoundError(
                f"No existe {input_csv}. Primero ejecuta la ingesta/scraping para generar el raw dataset."
            )
        df = pd.read_csv(input_csv)

    if df.empty:
        raise ValueError("El dataset raw está vacío. No hay nada que limpiar.")

    # --- Ensure expected columns
    # Common columns: date, source, title, text/content/body, url
    # We'll clean what exists.
    if "source" in df.columns:
        df["source"] = df["source"].apply(clean_source)

    if "title" in df.columns:
        df["title"] = df["title"].apply(clean_text)

    # Create / refresh title_clean
    if "title_clean" in df.columns:
        base = df["title_clean"].fillna(df.get("title", ""))
        df["title_clean"] = base.apply(make_title_clean)
    elif "title" in df.columns:
        df["title_clean"] = df["title"].apply(make_title_clean)

    # Clean main body fields if present
    for key in ("text", "content", "body", "summary"):
        if key in df.columns:
            df[key] = df[key].apply(clean_text)

    # Optional: normalize date column to YYYY-MM-DD if exists
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        except Exception:
            # leave as-is if parsing fails
            pass

    # Optional: drop exact duplicates by (date, title_clean) if both exist
    if "date" in df.columns and "title_clean" in df.columns:
        df = df.drop_duplicates(subset=["date", "title_clean"], keep="first")

    # --- Write
    if db is not None:
        if hasattr(db, "write_table"):
            db.write_table("news_clean", df)
        elif hasattr(db, "write_df"):
            db.write_df("news_clean", df)
        else:
            raise TypeError(
                "db fue provisto pero no tiene métodos write_table/write_df."
            )
    else:
        # Use utf-8-sig for Excel-friendly accent handling on Windows
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"✔ Cleaning OK: {len(df)} registros limpios")
    if db is None:
        print(f"✔ Guardado: {output_csv}")

    return df
