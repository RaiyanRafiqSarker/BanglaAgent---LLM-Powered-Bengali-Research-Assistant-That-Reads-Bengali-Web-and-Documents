import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
VECTORSTORE_DIR = DATA_DIR / "vectorstores"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

TOP_K_RETRIEVAL = 5
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
MAX_WEB_RESULTS = 5

MAX_PDF_PAGES = 500
MAX_CHUNK_TOKENS = 1000
REQUEST_TIMEOUT = 15

MIN_RELEVANCE_SCORE = 0.15
MIN_LEXICAL_OVERLAP = 0.1
MAX_EVIDENCE_CHUNKS = 10

PDF_SPECIFIC_PATTERNS = [
    "এই PDF",
    "PDF অনুযায়ী",
    "এই ডকুমেন্ট",
    "এই পিডিএফ",
    "পিডিএফ অনুযায়ী",
    "this PDF",
    "from this PDF",
    "according to the PDF",
    "uploaded PDF",
    "from the PDF",
    "PDF থেকে",
    "ডকুমেন্ট থেকে",
    "এই ফাইল",
    "ফাইল অনুযায়ী",
    "আপলোড করা PDF",
    "আপলোডেড PDF",
    "এই রিপোর্ট",
    "রিপোর্ট অনুযায়ী",
]

WEB_EXPLICIT_PATTERNS = [
    "ওয়েব",
    "web",
    "latest",
    "সাম্প্রতিক",
    "news",
    "সংবাদ",
    "খবর",
    "তুলনা",
    "comparison",
    "compare",
]

FALLBACK_NO_PDF_EVIDENCE = (
    "আপলোড করা PDF থেকে প্রাসঙ্গিক তথ্য পাওয়া যায়নি। "
    "আমি ওয়েব থেকে অনুমান করে উত্তর দিচ্ছি না।"
)

FALLBACK_NO_EVIDENCE = (
    "আমি নির্ভরযোগ্য সূত্রে এই তথ্যটি পাইনি। "
    "অনুগ্রহ করে আরেকটি সূত্র বা PDF দিন।"
)

FALLBACK_PDF_UNREADABLE = (
    "PDF থেকে টেক্সট পড়া যায়নি। "
    "এটি স্ক্যান করা বা ইমেজ-ভিত্তিক PDF হতে পারে।"
)
