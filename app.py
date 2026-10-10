"""Step 7: the chat page.

Run with: streamlit run app.py
"""

import os

import streamlit as st

from ragbot.answer import answer, extract_only_answer, get_api_key, make_client
from ragbot.chunking import load_chunks
from ragbot.config import DOCS_DIR, MAX_QUESTION_CHARS, MAX_QUESTIONS_PER_VISIT, MODEL, TOP_K
from ragbot.fetch import fetch_all
from ragbot.search import SearchIndex

st.set_page_config(page_title="Grid Guide")

EXAMPLES = [
    "What is a regional transmission organization?",
    "Why is electricity transmitted at high voltage?",
    "What is demand response?",
]

@st.cache_resource(show_spinner="Building the search index...")
def get_index() -> SearchIndex:
    return SearchIndex(load_chunks())

def find_api_key() -> str | None:
    """Look in the environment first, then in Streamlit's secrets."""
    key = get_api_key()
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY") or None
    except Exception: # no secrets file at all
        return None

@st.cache_resource
def get_client(api_key: str):
    return make_client(api_key)

def show_sources(hits) -> None:
    if not hits:
        return
    with st.expander(f"Sources ({len(hits)})"):
        for number, hit in enumerate(hits, start=1):
            preview = " ".join(hit.chunk.text.split()[:45])
            st.markdown(f"**[{number}] [{hit.chunk.title}]({hit.chunk.url})** · match {hit.score:.2f}")
            st.caption(preview + "...")

# ---------- first run: make sure the articles are downloaded ----------
if not any(DOCS_DIR.glob("*.txt")):
    with st.spinner("First run: downloading the articles from Wikipedia..."):
        totals = fetch_all()
    if totals["saved"] == 0:
        st.error("Could not download the articles. Check the internet connection and reload.")
        st.stop()

index = get_index()
api_key = find_api_key()
client = get_client(api_key) if api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = [] # each item: role, text, hits
    st.session_state.asked = 0

# ---------- sidebar ----------
with st.sidebar:
    st.header("About")
    articles = len({chunk.title for chunk in index.chunks})
    st.write(f"Answers come from {articles} Wikipedia articles about the power grid, split into {len(index.chunks):,} searchable pieces.")
    if client:
        st.success(f"Answers written by {MODEL}")
    else:
        st.info("Search-only mode: no API key found, so the best passage is shown instead of a written answer.")
    st.caption(f"Questions this visit: {st.session_state.asked} of {MAX_QUESTIONS_PER_VISIT}")
    st.caption("Article text is from Wikipedia, licensed CC BY-SA 4.0.")

# ---------- page ----------
st.title("Grid Guide")
st.caption("Ask how the electric power grid works. Every answer cites its sources.")

picked = None
if not st.session_state.messages:
    columns = st.columns(len(EXAMPLES))
    for column, example in zip(columns, EXAMPLES):
        if column.button(example):
            picked = example

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        show_sources(message["hits"])

typed = st.chat_input("Ask a question about the power grid")
question = picked or typed

if question:
    question = question.strip()[:MAX_QUESTION_CHARS]
    st.session_state.messages.append({"role": "user", "text": question, "hits": []})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if st.session_state.asked >= MAX_QUESTIONS_PER_VISIT:
            hits, reply = [], "You have reached the question limit for this visit. Reload the page to start again."
        else:
            st.session_state.asked += 1
            hits = index.search(question, top_k=TOP_K)
            try:
                with st.spinner("Thinking..."):
                    reply = answer(question, hits, client)
            except Exception as error: # the model call failed: fall back to search results
                reply = f"The language model is unavailable right now ({type(error).__name__}), so here is the best passage.\n\n"
                reply += extract_only_answer(hits)
        st.markdown(reply)
        show_sources(hits)
    st.session_state.messages.append({"role": "assistant", "text": reply, "hits": hits})