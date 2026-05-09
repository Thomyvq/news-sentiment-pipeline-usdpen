import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
import pandas as pd


def _get(url: str, user_agent: str, timeout: int):
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


def _extract_published_at(soup):
    candidates = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "article:published_time"}),
        ("meta", {"name": "pubdate"}),
        ("meta", {"name": "date"}),
        ("meta", {"property": "og:updated_time"}),
        ("meta", {"name": "parsely-pub-date"}),
        ("meta", {"itemprop": "datePublished"}),
    ]

    for tag, attrs in candidates:
        m = soup.find(tag, attrs=attrs)
        if m and m.get("content"):
            return m.get("content")

    t = soup.find("time")
    if t:
        return t.get("datetime") or t.get_text(" ", strip=True)

    return ""


def scrape_reuters_business(
    list_url: str,
    user_agent: str,
    timeout: int,
    sleep_sec: float,
    max_items: int
):
    html = _get(list_url, user_agent, timeout)
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.select("a[href]"):
        href = a.get("href", "")

        if not href:
            continue

        if "/article/" in href or href.startswith("/world/") or href.startswith("/business/"):
            full = urljoin("https://www.reuters.com", href)

            if full not in links:
                links.append(full)

        if len(links) >= max_items:
            break

    items = []

    for url in links[:max_items]:
        try:
            time.sleep(sleep_sec)

            art = _get(url, user_agent, timeout)
            s2 = BeautifulSoup(art, "html.parser")

            title = s2.find("h1").get_text(" ", strip=True) if s2.find("h1") else ""
            paras = [p.get_text(" ", strip=True) for p in s2.select("p")]
            body = " ".join(paras[:20])

            items.append({
                "url": url,
                "title": title,
                "summary": body,
                "published_at": _extract_published_at(s2),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "Reuters Business",
            })

        except Exception as e:
            print(f"[Reuters] Error en {url}: {e}")
            continue

    return items


def scrape_bloomberglinea_tag(
    list_url: str,
    user_agent: str,
    timeout: int,
    sleep_sec: float,
    max_items: int
):
    html = _get(list_url, user_agent, timeout)
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.select("a[href]"):
        href = a.get("href", "")

        if not href:
            continue

        if href.startswith("/"):
            full = urljoin("https://www.bloomberglinea.com", href)
        else:
            full = href

        if "bloomberglinea.com" in full and "/tags/" not in full:
            if full not in links:
                links.append(full)

        if len(links) >= max_items:
            break

    items = []

    for url in links[:max_items]:
        try:
            time.sleep(sleep_sec)

            art = _get(url, user_agent, timeout)
            s2 = BeautifulSoup(art, "html.parser")

            title = s2.find("h1").get_text(" ", strip=True) if s2.find("h1") else ""
            paras = [p.get_text(" ", strip=True) for p in s2.select("p")]
            body = " ".join(paras[:25])

            items.append({
                "url": url,
                "title": title,
                "summary": body,
                "published_at": _extract_published_at(s2),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "Bloomberg Línea",
            })

        except Exception as e:
            print(f"[Bloomberg Línea] Error en {url}: {e}")
            continue

    return items


def scrape_gdelt_news(
    query: str,
    start_date: str,
    end_date: str,
    max_records: int = 250
):
    """
    Scraper histórico usando GDELT 2.1 DOC API.

    Permite obtener noticias históricas por rango de fechas.
    Formato:
    start_date = 'YYYY-MM-DD'
    end_date   = 'YYYY-MM-DD'
    """

    start_dt = pd.to_datetime(start_date).strftime("%Y%m%d000000")
    end_dt = pd.to_datetime(end_date).strftime("%Y%m%d235959")

    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "startdatetime": start_dt,
        "enddatetime": end_dt,
        "maxrecords": max_records,
        "sort": "HybridRel",
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()

    except Exception as e:
        print(f"[GDELT] Error consultando {start_date} → {end_date}: {e}")
        return []

    articles = data.get("articles", [])
    items = []

    for a in articles:
        published_at = a.get("seendate", "")

        items.append({
            "url": a.get("url", ""),
            "title": a.get("title", ""),
            "summary": a.get("title", ""),
            "published_at": published_at,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": a.get("sourceCommonName", "GDELT"),
        })

    return items


def scrape_gdelt_news_by_day(
    query: str,
    start_date: str,
    end_date: str,
    max_records_per_day: int = 100,
    sleep_sec: float = 1.0
):
    """
    Scraping histórico diario para generar una serie más continua.

    Recorre día por día entre start_date y end_date.
    """

    start = pd.to_datetime(start_date).date()
    end = pd.to_datetime(end_date).date()

    all_items = []
    current = start

    while current <= end:
        day_str = current.strftime("%Y-%m-%d")

        print(f"[GDELT] Scraping día: {day_str}")

        items = scrape_gdelt_news(
            query=query,
            start_date=day_str,
            end_date=day_str,
            max_records=max_records_per_day
        )

        all_items.extend(items)

        time.sleep(sleep_sec)
        current = current + timedelta(days=1)

    df = pd.DataFrame(all_items)

    if df.empty:
        return []

    df = df.drop_duplicates(subset=["url"])
    return df.to_dict("records")