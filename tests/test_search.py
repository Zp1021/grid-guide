import pytest

from ragbot.chunking import load_chunks
from ragbot.search import SearchIndex

@pytest.fixture
def index(docs_folder):
    return SearchIndex(load_chunks(docs_folder))

def test_finds_the_right_article(index):
    hits = index.search("How many books can I borrow?")
    assert hits[0].chunk.title == "Borrowing books"

def test_results_are_sorted_best_first(index):
    hits = index.search("When does the library open on Saturdays?", min_score=0.0)
    scores = [hit.score for hit in hits]
    assert scores == sorted(scores, reverse=True)
    assert hits[0].chunk.title == "Library hours"

def test_off_topic_question_returns_nothing(index):
    assert index.search("What is the capital of France?") == []

def test_top_k_limits_the_number_of_results(index):
    assert len(index.search("library", top_k=2, min_score=0.0)) <= 2

def test_empty_index_is_refused():
    with pytest.raises(ValueError):
        SearchIndex([])