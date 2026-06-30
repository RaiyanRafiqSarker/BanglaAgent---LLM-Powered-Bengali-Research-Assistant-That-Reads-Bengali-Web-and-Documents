# BanglaAgent 🔍

**Bengali Research Assistant for Web, PDFs, and Source-backed Answers

BanglaAgent is an agentic AI research assistant built for Bangladeshi journalists, students, researchers, and policy readers. Think of it as "Perplexity AI for Bengali" — it searches Bengali web sources, reads PDFs, retrieves relevant information, summarizes in Bengali, answers follow-up questions with citations, and generates podcast scripts.

---

## Features

- **Bengali Web Search** — Searches Prothom Alo, Daily Star Bangla, and general Bengali web sources
- **PDF Analysis** — Upload any PDF, extract text, and ask questions about it
- **RAG Pipeline** — FAISS-powered vector retrieval combining PDF and web evidence
- **Citation System** — Every claim is backed by source citations (page numbers for PDFs, URLs for web)
- **Hallucination Guard** — Refuses to fabricate answers when evidence is missing
- **Podcast Script Generator** — Creates Bengali podcast scripts from evidence
- **Professional UI** — Modern, dark-themed SaaS-style Gradio interface
- **Multi-language Output** — Bengali, English, or mixed answers

## Screenshots

*Coming soon — run the app to see the professional UI*

## Tech Stack

| Component | Technology |
| --- | --- |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | FAISS (local) |
| Web Search | DuckDuckGo (free, no API key) |
| Scraping | BeautifulSoup4 + requests |
| PDF | PyMuPDF (fitz) |
| Frontend | Gradio Blocks + Custom CSS |
| Orchestration | Custom ReAct-style agent |

## Project Structure

```text
BanglaAgent/
├── app.py                  # Gradio frontend
├── config.py               # Configuration constants
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── README.md
├── src/
│   ├── __init__.py
│   ├── llm.py              # OpenAI wrapper (chat + embeddings)
│   ├── agent.py            # BanglaAgent orchestrator
│   ├── tools/
│   │   ├── web_search.py   # Bengali web search + scraping
│   │   ├── pdf_reader.py   # PDF extraction + FAISS indexing
│   │   ├── retriever.py    # Combined evidence retrieval
│   │   ├── summarizer.py   # Evidence-based summarization
│   │   └── podcast.py      # Podcast script generation
│   └── utils/
│       ├── bengali_text.py  # Bengali text cleaning
│       ├── citations.py     # Citation formatting + validation
│       ├── chunking.py      # Text chunking for RAG
│       └── ui_helpers.py    # UI formatting helpers
├── data/
│   ├── uploads/            # Uploaded PDFs
│   └── vectorstores/       # FAISS indexes
└── tests/
    ├── test_chunking.py
    ├── test_citations.py
    └── test_empty_retrieval.py
```

## Setup

### 1. Clone and enter the project

```bash
cd BanglaAgent
```

### 2. Create a virtual environment

#### Mac/Linux

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key:

```env
OPENAI_API_KEY=sk-your-real-key-here
```

You can get an API key from [platform.openai.com](https://platform.openai.com/api-keys).

### 5. Run the app

```bash
python app.py
```

Open your browser at <http://localhost:7860>

## Usage

### Asking Questions

1. Type a question in Bengali or English
2. Click "🚀 অনুসন্ধান শুরু করুন" or press Enter
3. View the answer, citations, evidence, and limitations in the tabs

### Using PDFs

1. Upload a PDF using the left sidebar
2. Make sure "📄 আপলোডেড PDF ব্যবহার" is checked
3. Ask a question — the agent will search the PDF content and cite page numbers

### Web Search

Web search is enabled by default. The agent searches:

- Prothom Alo (প্রথম আলো)
- Daily Star Bangla
- General Bengali web sources via DuckDuckGo

No paid search API needed.

### Podcast Mode

Select "Podcast Script" from the output mode dropdown, or check "🎙️ পডকাস্ট ফরম্যাট" to get a Bengali podcast script.

### Example Questions

- বাংলাদেশ বাজেট সহজ ভাষায় ব্যাখ্যা করো
- এই PDF থেকে মূল পয়েন্টগুলো বের করো
- এই বিষয়ে একটি বাংলা পডকাস্ট স্ক্রিপ্ট বানাও
- Prothom Alo ও Daily Star থেকে সাম্প্রতিক তথ্য দাও

## How Citations Work

- **PDF citations**: `[PDF: filename.pdf, page 12]`
- **Web citations**: `[Source: Article Title, URL]`
- Every factual claim links back to retrieved evidence
- If no evidence supports a claim, the agent says so explicitly

## Running Tests

```bash
pytest tests/ -v
```

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `OPENAI_API_KEY not set` | Add your key to `.env` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| PDF not processing | Ensure PDF contains text (not scanned images) |
| Web search returns nothing | Check internet connection; DuckDuckGo may rate-limit |
| Port 7860 in use | Kill the process or change port in `app.py` |

## Limitations

- Scanned/image-based PDFs are not supported (no OCR)
- Web search depends on DuckDuckGo availability
- Bengali article scraping quality varies by website structure
- Answers are limited by the quality and quantity of retrieved evidence
- Large PDFs (500+ pages) are truncated

## Responsible Scraping

BanglaAgent scrapes publicly available news articles for research purposes. It:

- Sends standard browser User-Agent headers
- Respects timeouts and does not flood servers
- Only fetches a small number of articles per query
- Does not bypass paywalls or authentication

Please use responsibly and respect website terms of service.

## License

This project is for educational and research purposes.
