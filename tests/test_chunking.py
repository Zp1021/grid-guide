import pytest

from ragbot.chunking import load_chunks, split_words, strip_headings

def numbered_words(count: int) -> str:
    """'w0 w1 w2 ...' so every word's position is easy to check."""
    return " ".join(f"w{i}" for i in range(count))

def test_short_text_is_one_chunk():
    assert split_words("just a few words", size=10, overlap=2) == ["just a few words"]

def test_chunks_overlap_by_the_requested_number_of_words():
    pieces = split_words(numbered_words(25), size=10, overlap=3)
    first, second = pieces[0].split(), pieces[1].split()
    assert len(first) == 10
    assert first[-3:] == second[:3]         # the last 3 words are repeated

def test_no_words_are_lost():
    pieces = split_words(numbered_words(95), size=20, overlap=5)
    seen = {word for piece in pieces for word in piece.split()}
    assert seen == {f"w{i}" for i in range(95)}

def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        split_words("some words", size=5, overlap=5)

def test_headings_become_plain_text():
    assert strip_headings("== Renewals ==\nText.") == "Renewals.\nText."

def test_load_chunks_keeps_title_and_link(docs_folder):
    chunks = load_chunks(docs_folder)
    titles = {chunk.title for chunk in chunks}
    assert titles == {"Library hours", "Borrowing books", "Study rooms"}
    assert all(chunk.url.startswith("https://en.wikipedia.org/wiki/") for chunk in chunks)