"""Step 2: download the articles from Wikipedia and save them as text files.

Run with: python -m ragbot.fetch
"""

import re
from pathlib import Path

import requests

from ragbot.config import ARTICLES, DOCS_DIR, USER_AGENT, WIKI_API

# Sections at the end of an article that are lists of links, not knowledge
END_SECTIONS = ["See also", "References", "Notes", "Further reading", "External links", "Citations"]

def slug(title: str) -> str:
    """Turn an article title into a safe file name."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

def article_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")

def clean_text(text: str) -> str:
    """Cut the link sections off the end and tidy up blank lines."""
    for name in END_SECTIONS:
        match = re.search(rf"\n==+\s*{re.escape(name)}\s*==+", text)
        if match:
            text = text[: match.start()]
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def fetch_article(title: str, api: str = WIKI_API) -> str | None:
    """Return the plain text of one article, or None if it cannot be fetched."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": title,
        "format": "json",
        "formatversion": 2,
    }
    try:
        response = requests.get(api, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        pages = response.json()["query"]["pages"]
    except (requests.RequestException, KeyError, ValueError):
        return None
    if not pages or pages[0].get("missing") or not pages[0].get("extract"):
        return None
    return clean_text(pages[0]["extract"])

def save_article(title: str, text: str, folder: Path = DOCS_DIR) -> Path:
    """Save one article. Line 1 is the title, line 2 the link, then the text."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slug(title)}.txt"
    path.write_text(f"{title}\n{article_url(title)}\n\n{text}\n", encoding="utf-8")
    return path

def fetch_all(titles: list[str] = ARTICLES, folder: Path = DOCS_DIR, api: str = WIKI_API) -> dict[str, int]:
    """Download every article and count what happened."""
    counts = {"saved": 0, "failed": 0}
    for title in titles:
        text = fetch_article(title, api)
        if text is None:
            counts["failed"] += 1
            print(f"FAILED {title}")
        else:
            save_article(title, text, folder)
            counts["saved"] += 1
            print(f"saved {title} ({len(text.split()):,} words)")
    return counts

if __name__ == "__main__":
    totals = fetch_all()
    print(totals)
    if totals["saved"] == 0:
        raise SystemExit("No articles were saved. See Troubleshooting in the guide.")