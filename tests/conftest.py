"""Shared test data: a tiny made-up knowledge base about a town library."""
import pytest

from ragbot.fetch import save_article

LIBRARY_DOCS = {
    "Library hours": (
        "The Maple Town Library opens at nine in the morning on weekdays and closes at eight in the evening. "
        "On Saturdays the library opens at ten and closes at five. The library is closed on Sundays and on public holidays."
    ),
    "Borrowing books": (
        "Members may borrow up to ten books at a time. Each loan lasts three weeks and can be renewed twice."
        "A late fee of ten cents per day applies to overdue books.\n\n== Renewals ==\n"
        "Renewals can be made online, by telephone, or at the front desk."
    ),
    "Study rooms": (
        "The library has four study rooms on the second floor. Rooms can be reserved for two hours at a time. "
        "Each study room has a whiteboard, a large table, and seating for six people."
    ),
}

@pytest.fixture
def docs_folder(tmp_path):
    """A temporary folder holding the three library articles."""
    for title, text in LIBRARY_DOCS.items():
        save_article(title, text, tmp_path)
    return tmp_path