# src/ingest/runner.py

import uuid
import pandas as pd

from ..utils.hashing import sha256_text
from ..utils.text import strip_html, normalize_text
from .rss import fetch_rss
from .scrapers import (
    scrape_reuters_business,
    scrape_bloomberglinea_tag,
    scrape_gdelt_news_by_day,
)


def run_ingestion(db, sources_cfg, pipeline_cfg, start_date=None, end_date=None) -> pd.DataFrame:
    """
    Ejecuta la ingesta de noticias desde las fuentes configuradas.

    Soporta:
    - RSS
    - Scraping Reuters
    - Scraping Bloomberg Línea
    - GDELT histórico diario

    Retorna un DataFrame con las noticias recolectadas en la ejecución.
    """

    scfg = pipeline_cfg["scraping"]
    ua = scfg["user_agent"]
    timeout = int(scfg["timeout_sec"])
    sleep_sec = float(scfg["sleep_sec"])
    max_items = int(scfg["max_items_per_source"])

    # Fechas por defecto desde config
    if start_date is None:
        start_date = pipeline_cfg.get("date_range", {}).get("start", "2026-01-01")

    if end_date is None:
        end_date = pipeline_cfg.get("date_range", {}).get("end", "2026-05-08")

    rows = []

    for src in sources_cfg.get("sources", []):
        stype = src.get("type")
        url = src.get("url")

        if not stype:
            continue

        print(f"▶ Fuente: {src.get('name', stype)} [{stype}]")

        try:
            if stype == "rss":
                if not url:
                    continue
                items = fetch_rss(url)

            elif stype == "scrape_reuters_business":
                if not url:
                    continue
                items = scrape_reuters_business(
                    url,
                    ua,
                    timeout,
                    sleep_sec,
                    max_items
                )

            elif stype == "scrape_bloomberglinea_tag":
                if not url:
                    continue
                items = scrape_bloomberglinea_tag(
                    url,
                    ua,
                    timeout,
                    sleep_sec,
                    max_items
                )

            elif stype == "gdelt_daily":
                query = src.get(
                    "query",
                    '(Peru OR "Peruvian sol" OR "USD PEN" OR BCRP OR "exchange rate Peru" OR "Peru inflation")'
                )

                items = scrape_gdelt_news_by_day(
                    query=query,
                    start_date=start_date,
                    end_date=end_date,
                    max_records_per_day=max_items,
                    sleep_sec=sleep_sec,
                )

            else:
                print(f"⚠ Fuente ignorada. Tipo no soportado: {stype}")
                continue

        except Exception as e:
            print(f"⚠ Error en fuente {src.get('name', stype)}: {e}")
            continue

        for it in items or []:
            if not it.get("url"):
                continue

            title = normalize_text(strip_html(it.get("title", "")))
            body = normalize_text(strip_html(it.get("summary", "")))

            if not title and not body:
                continue

            content_hash = sha256_text(title + "||" + body)

            # ID estable para evitar duplicados entre ejecuciones
            news_id = sha256_text(it["url"])[:32]

            row = {
                "news_id": news_id,
                "source": it.get("source") or src.get("name", ""),
                "url": it["url"],
                "published_at": it.get("published_at", "") or "",
                "fetched_at": it.get("fetched_at", "") or "",
                "title_raw": title,
                "body_raw": body,
                "content_hash": content_hash,
                "lang_hint": src.get("lang_hint", "auto"),
                "reliability_weight": float(src.get("reliability_weight", 1.0)),
            }

            try:
                db.upsert("raw_news", row, key="news_id")
            except Exception:
                pass

            rows.append(row)

    df_raw = pd.DataFrame(rows)

    if not df_raw.empty:
        df_raw = df_raw.drop_duplicates(subset=["url"])
        df_raw = df_raw.drop_duplicates(subset=["content_hash"])

    return df_raw


def run_ingest(db, sources_cfg, pipeline_cfg, start_date=None, end_date=None):
    return run_ingestion(
        db,
        sources_cfg,
        pipeline_cfg,
        start_date=start_date,
        end_date=end_date,
    )