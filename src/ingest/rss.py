import feedparser
from datetime import datetime, timezone

def fetch_rss(url: str):
    feed = feedparser.parse(url)
    items = []
    for e in getattr(feed, "entries", []):
        published = getattr(e, "published", None) or getattr(e, "updated", None) or ""
        items.append({
            "url": getattr(e, "link", None),
            "title": getattr(e, "title", ""),
            "summary": getattr(e, "summary", "") or getattr(e, "description", ""),
            "published_at": published,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        })
    return items
