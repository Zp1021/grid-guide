# Grid Guide

A question-answering assistant about the electric power grid. It searches a small library of Wikipedia articles, then has a language model write an answer that cites its sources.

**Live demo:** [(https://grid-guide-m2sysqrhzlaazenuso57t6.streamlit.app/)]

![tests](https://github.com/Zp1021/grid-guide/actions/workflows/tests.yml/badge.svg)

## Results

Measured with `python -m ragbot.evaluate` on October 8, 2026.

| Measure | Result |
| --- | --- |
| Knowledge base | 16 articles, 479 chunks, about 84,982 words |
| Test questions with a known answer | 20 |
| Right article is the top result | 70% |
| Right article is in the top 4 | 100% |
| Mean reciprocal rank | 0.83 |
| Median search time | 0.4 ms |
| Off-topic questions refused by search | 4 of 4 |

## How it works

1. `ragbot/fetch.py` downloads the articles through Wikipedia's public API.
2. `ragbot/chunking.py` cuts each article into 180-word pieces that overlap by 40 words.
3. `ragbot/search.py` builds a TF-IDF index and returns the best-matching pieces for a question.
4. `ragbot/answer.py` sends those pieces, numbered, to Claude with instructions to answer only from them and cite each fact.
5. `ragbot/evaluate.py` scores the search against 24 test questions: 20 with a known source article and 4 off-topic.
6. `app.py` is the Streamlit chat page.

If the search finds nothing relevant, the assistant says so without calling the model. If no API key is set, it runs in search-only mode and shows the best passage.

## Run it yourself

```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ragbot.fetch
python -m ragbot.evaluate
streamlit run app.py
```

Set `ANTHROPIC_API_KEY` in your environment to get written answers.

## Tests

```
pytest
```

22 tests cover file handling, chunk overlap, search ranking, the off-topic refusal, and the prompt. The model is replaced by a stand-in during tests, so they need no key and cost nothing.

## Limits

- Search matches words, not meaning. A question phrased with different vocabulary than the article can miss.
- Each question is answered on its own; the assistant does not remember earlier turns.
- The knowledge base is 16 articles and is only as accurate as those articles.
- The evaluation checks whether the right article is retrieved, not the exact passage or the quality of the written answer.

## Data

Article text comes from Wikipedia and is licensed CC BY-SA 4.0. Each answer links to its source articles.