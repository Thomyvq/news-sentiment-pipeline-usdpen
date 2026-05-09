import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

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

def scrape_reuters_business(list_url: str, user_agent: str, timeout: int, sleep_sec: float, max_items: int):
    html = _get(list_url, user_agent, timeout)
    soup = BeautifulSoup(html, "html.parser")

    # Reuters cambia DOM; buscamos links a /article/ o /world/ etc. desde el listado
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
            # Título
            title = (s2.find("h1").get_text(" ", strip=True) if s2.find("h1") else "")
            # Cuerpo: concatenar párrafos
            paras = [p.get_text(" ", strip=True) for p in s2.select("p")]
            body = " ".join(paras[:20])  # cap
            items.append({
                "url": url,
                "title": title,
                "summary": body,
                "published_at": "",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            continue

    return items

def scrape_bloomberglinea_tag(list_url: str, user_agent: str, timeout: int, sleep_sec: float, max_items: int):
    html = _get(list_url, user_agent, timeout)
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if not href:
            continue
        # Bloomberg Línea suele usar rutas relativas /202x/...
        if href.startswith("/"):
            full = urljoin("https://www.bloomberglinea.com", href)
        else:
            full = href
        if "bloomberglinea.com" in full and "/tags/" not in full:
            # heurística: evitar páginas de tag dentro del tag
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
            title = (s2.find("h1").get_text(" ", strip=True) if s2.find("h1") else "")
            paras = [p.get_text(" ", strip=True) for p in s2.select("p")]
            body = " ".join(paras[:25])
            items.append({
                "url": url,
                "title": title,
                "summary": body,
                "published_at": "",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            continue

    return items
