"""Settings used by every other file. Change things here, not in ten places."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# One text file per article
DOCS_DIR = ROOT / "data" / "docs"

EVAL_FILE = ROOT / "evalset" / "questions.json"

# Where the articles come from: Wikipedia's public api (no key needed)
WIKI_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "grid-guide-student-project/1.0 (https://github.com/Zp1021/grid-guide)"

# The articles that make up the assistant's knowledge
ARTICLES = [
    "Electrical grid",
    "Electricity market",
    "Regional transmission organization (North America)",
    "New York Independent System Operator",
    "PJM Interconnection",
    "Demand response",
    "Electric power transmission",
    "Electric power distribution",
    "Base load",
    "Peaking power plant",
    "Smart grid",
    "Net metering",
    "Power outage",
    "Grid energy storage",
    "Federal Energy Regulatory Commission",
    "North American Electric Reliability Corporation",
]

# Chunking: how big each searchable piece of text is, in words
CHUNK_WORDS = 180
CHUNK_OVERLAP = 40

# Search: how many pieces to hand to the model, and the weakest match we accept
TOP_K = 4
MIN_SCORE = 0.08

# The lange model. Haiku is Anthropic's fastest, lowest-cost model
MODEL = "claude-haiku-4-5-20251001"
MAX_ANSWER_TOKENS = 500

# Safety limits for the public demo
MAX_QUESTION_CHARS = 300
MAX_QUESTIONS_PER_VISIT = 15