"""Step 6: measure how well the search works, with real numbers.

Run with: python -m ragbot.evaluate
"""

import json
import statistics
import time
from pathlib import Path

from ragbot.chunking import load_chunks
from ragbot.config import EVAL_FILE, TOP_K
from ragbot.search import SearchIndex

def load_questions(path: Path = EVAL_FILE) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))

def first_correct_rank(index: SearchIndex, question: str, expected: list[str], top_k: int) -> int | None:
    """Position (1 = top) of the first result from an expected article, or None."""
    for rank, hit in enumerate(index.search(question, top_k=top_k), start=1):
        if hit.chunk.title in expected:
            return rank
    return None

def evaluate(index: SearchIndex, questions: list[dict], top_k: int = TOP_K) -> dict:
    """Score the search on questions whose correct article we already know."""
    answerable = [q for q in questions if q["expected"]]
    off_topic = [q for q in questions if not q["expected"]]

    ranks, times = [], []
    for item in answerable:
        start = time.perf_counter()
        ranks.append(first_correct_rank(index, item["question"], item["expected"], top_k))
        times.append((time.perf_counter() - start) * 1000)
        
    refused = sum(1 for item in off_topic if not index.search(item["question"], top_k=top_k))
    total = len(answerable)
    return {
        "questions": total,
        "top_1_rate": sum(1 for r in ranks if r == 1) / total if total else 0.0,
        "top_k_rate": sum(1 for r in ranks if r is not None) / total if total else 0.0,
        "mean_reciprocal_rank": sum(1 / r for r in ranks if r) / total if total else 0.0,
        "median_search_ms": statistics.median(times) if times else 0.0,
        "off_topic_questions": len(off_topic),
        "off_topic_refused": refused,
        "missed": [q["question"] for q, r in zip(answerable, ranks) if r is None],
    }

if __name__ == "__main__":
    chunks = load_chunks()
    index = SearchIndex(chunks)
    articles = len({chunk.title for chunk in chunks})
    words = sum(len(chunk.text.split()) for chunk in chunks)
    print(f"Knowledge base: {articles} articles, {len(chunks):,} chunks, about {words:,} words")

    result = evaluate(index, load_questions())
    print(f"Questions with a known answer: {result['questions']}")
    print(f"Right article is the top result: {result['top_1_rate']:.0%}")
    print(f"Right article is in the top {TOP_K}: {result['top_k_rate']:.0%}")
    print(f"Mean reciprocal rank: {result['mean_reciprocal_rank']:.2f}")
    print(f"Median search time: {result['median_search_ms']:.1f} ms")
    print(f"Off-topic questions refused: {result['off_topic_refused']} of {result['off_topic_questions']}")
    for question in result["missed"]:
        print(f" MISSED: {question}")