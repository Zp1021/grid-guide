"""Step 3: read the saved articles and cut them into small overlapping pieces."""
import re
from dataclasses import dataclass
from pathlib import Path

from ragbot.config import CHUNK_OVERLAP, CHUNK_WORDS, DOCS_DIR

@dataclass
class Chunk:
    """One searchable piece of one article."""
    title: str # which article it came from
    url: str # link to that article
    position: int # 0 for the first piece of the article, 1 for the next, ...
    text: str

def read_article(path: Path) -> tuple[str, str, str]:
    """Return (title, url, text) from a saved article file."""
    lines = path.read_text(encoding="utf-8").split("\n")
    title, url = lines[0].strip(), lines[1].strip()
    text = "\n".join(lines[2:]).strip()
    return title, url, text

def strip_headings(text: str) -> str:
    """Turn '== History ==' into 'History.' so headings read as plain text."""
    return re.sub(r"^=+\s*(.*?)\s*=+\s*$", r"\1.", text, flags=re.MULTILINE)

def split_words(text: str, size: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Cut text into pieces of `size` words. Each piece repeats the last
    `overlap` words of the one before it."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    words = text.split()
    pieces, start = [], 0
    while start < len(words):
        pieces.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
        start += size - overlap
    return pieces

def load_chunks(folder: Path = DOCS_DIR) -> list[Chunk]:
    """Read every article in the folder and return all of its chunks."""
    chunks = []
    for path in sorted(folder.glob("*.txt")):
        title, url, text = read_article(path)
        for position, piece in enumerate(split_words(strip_headings(text))):
            chunks.append(Chunk(title=title, url=url, position=position, text=piece))
    return chunks