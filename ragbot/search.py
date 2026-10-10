"""Step 4: find the chunks that best match a question."""
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from ragbot.chunking import Chunk
from ragbot.config import MIN_SCORE, TOP_K

@dataclass
class Hit:
    """One search result: a chunk and how well it matched (0 to 1)."""
    chunk: Chunk
    score: float

class SearchIndex:
    """A TF-IDF index over all chunks."""
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("No chunks to index. Run the fetch step first.")
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            stop_words="english",                   # ignore words like "the" and "of"
            ngram_range=(1, 2),                     # single words and two-word phrases
            sublinear_tf=True,                      # a word used 10 times is not 10x as important
        )
        
        # Put the article title in front of each chunk so the topic always counts
        texts = [f"{chunk.title}. {chunk.text}" for chunk in chunks]
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, question: str, top_k: int = TOP_K, min_score: float = MIN_SCORE) -> list[Hit]:
        """Return up to top_k chunks, best first, leaving out weak matches."""
        question_vector = self.vectorizer.transform([question])
        scores = linear_kernel(question_vector, self.matrix) [0]
        best = scores.argsort()[::-1][:top_k]
        return [Hit(self.chunks[i], float(scores[i])) for i in best if scores[i] >= min_score]