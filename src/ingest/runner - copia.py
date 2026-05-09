# src/ingest/runner.py

import uuid
import pandas as pd

from ..utils.hashing import sha256_text
from ..utils.text import strip_html, normalize_text
from .rss import fetch_rss
from .scrapers import scrape_reuters_business, scrape_bloomberglinea_tag


def run_ingestion(db, sources_cfg, pipeline_cfg, start_date=None, end_date=None) -> pd.DataFrame:
    """
    Ejecuta la ingesta de noticias desde las fuentes configuradas y:
    - Inserta (upsert) cada noticia en DB (tabla: raw_news)
    - Retorna un DataFrame con las filas procesadas en esta ejecución

    start_date/end_date se dejan como parámetros opcionales para compatibilidad
    con pipelines que los pasan, aunque aquí no se filtra por fecha (depende de cada fuente).
    """
    scfg = pipeline_cfg["scraping"]
    ua = scfg["user_agent"]
    timeout = int(scfg["timeout_sec"])
    sleep_sec = float(scfg["sleep_sec"])
    max_items = int(scfg["max_items_per_source"])

    rows = []

    for src in sources_cfg.get("sources", []):
        stype = src.get("type")
        url = src.get("url")

        if not stype or not url:
            continue

        try:
            if stype == "rss":
                items = fetch_rss(url)
            elif stype == "scrape_reuters_business":
                items = scrape_reuters_business(url, ua, timeout, sleep_sec, max_items)
            elif stype == "scrape_bloomberglinea_tag":
                items = scrape_bloomberglinea_tag(url, ua, timeout, sleep_sec, max_items)
            else:
                continue
        except Exception:
            # Si una fuente falla, continúa con la siguiente
            continue

        for it in items or []:
            if not it.get("url"):
                continue

            title = normalize_text(strip_html(it.get("title", "")))
            body = normalize_text(strip_html(it.get("summary", "")))
            content_hash = sha256_text(title + "||" + body)

            row = {
                "news_id": str(uuid.uuid4()),
                "source": src.get("name", ""),
                "url": it["url"],
                "published_at": it.get("published_at", "") or "",
                "fetched_at": it.get("fetched_at", "") or "",
                "title_raw": title,
                "body_raw": body,
                "content_hash": content_hash,
                "lang_hint": src.get("lang_hint", "auto"),
                "reliability_weight": float(src.get("reliability_weight", 1.0)),
            }

            # Insert / upsert a DB (según tu implementación interna)
            try:
                db.upsert("raw_news", row, key="news_id")
            except Exception:
                # No tumbes el pipeline por un insert fallido
                pass

            rows.append(row)

    df_raw = pd.DataFrame(rows)
    return df_raw


# --- Compatibilidad: si en tu código antiguo llamabas run_ingest(...) ---
def run_ingest(db, sources_cfg, pipeline_cfg):
    return run_ingestion(db, sources_cfg, pipeline_cfg)
