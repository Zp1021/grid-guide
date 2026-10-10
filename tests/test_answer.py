from types import SimpleNamespace

from ragbot.answer import NOT_FOUND, SYSTEM_PROMPT, answer, build_prompt
from ragbot.chunking import Chunk
from ragbot.config import MODEL
from ragbot.search import Hit

class FakeClient:
    """Stands in for the Anthropic client so tests cost nothing and need no key."""

    def __init__(self, reply: str):
        self.reply = reply
        self.calls = []
        self.messages = self            # so client.messages.create(...) works

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.reply)])

def make_hits():
    hours = Chunk("Library hours", "https://example.org/hours", 0, "The library opens at nine.")
    rooms = Chunk("Study rooms", "https://example.org/rooms", 0, "There are four study rooms.")
    return [Hit(hours, 0.61), Hit(rooms, 0.22)]

def test_prompt_numbers_every_source_and_ends_with_the_question():
    prompt = build_prompt("When does it open?", make_hits())
    assert '<source number="1" title="Library hours">' in prompt
    assert '<source number="2" title="Study rooms">' in prompt
    assert prompt.endswith("Question: When does it open?")

def test_no_hits_means_no_model_call():
    client = FakeClient("should never be used")
    assert answer("Anything?", [], client) == NOT_FOUND
    assert client.calls == []           # the model was never asked

def test_without_a_client_the_best_passage_is_shown():
    text = answer("When does it open?", make_hits(), client=None)
    assert "Search-only mode" in text
    assert "Library hours" in text

def test_with_a_client_the_model_reply_is_returned():
    client = FakeClient("It opens at nine [1].")
    assert answer("When does it open?", make_hits(), client) == "It opens at nine [1]."
    call = client.calls[0]
    assert call["model"] == MODEL
    assert call["system"] == SYSTEM_PROMPT
    assert "The library opens at nine." in call["messages"][0]["content"]