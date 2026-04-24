import re
from bs4 import BeautifulSoup

def strip_html(text: str) -> str:
    soup = BeautifulSoup(text or "", "html.parser")
    return soup.get_text(" ", strip=True)

def normalize_text(text: str) -> str:
    t = text or ""
    t = re.sub(r"\s+", " ", t).strip()
    return t

def build_text(title: str, body: str) -> str:
    title = normalize_text(title)
    body = normalize_text(body)
    if title and body:
        return f"{title}. {body}"
    return title or body
