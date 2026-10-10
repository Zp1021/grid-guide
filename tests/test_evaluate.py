from ragbot.chunking import load_chunks
from ragbot.evaluate import evaluate, load_questions
from ragbot.search import SearchIndex

QUESTIONS = [
    {"question": "How many books can I borrow?", "expected": ["Borrowing books"]},
    {"question": "Can I reserve a study room?", "expected": ["Study rooms"]},
    {"question": "What is the capital of France?", "expected": []},
]

def test_evaluate_scores_known_questions(docs_folder):
    result = evaluate(SearchIndex(load_chunks(docs_folder)), QUESTIONS)
    assert result["questions"] == 2
    assert result["top_1_rate"] == 1.0
    assert result["mean_reciprocal_rank"] == 1.0
    assert result["off_topic_refused"] == 1
    assert result["missed"] == []

def test_a_wrong_expected_article_counts_as_a_miss(docs_folder):
    questions = [{"question": "How many books can I borrow?", "expected": ["Library hours"]}]
    result = evaluate(SearchIndex(load_chunks(docs_folder)), questions, top_k=1)
    assert result["top_1_rate"] == 0.0
    assert len(result["missed"]) == 1

def test_the_real_question_file_is_well_formed():
    questions = load_questions()
    assert len(questions) >= 20
    assert all(isinstance(q["question"], str) and isinstance(q["expected"], list) for q in questions)
