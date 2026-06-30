import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.retriever import retrieve_combined_context
from src.tools.summarizer import summarize_evidence
from src.tools.podcast import create_podcast_script
from src.utils.ui_helpers import NO_EVIDENCE_MSG


def test_retrieve_no_sources():
    result = retrieve_combined_context(
        query="test query",
        pdf_vectorstore=None,
        web_results=None,
        top_k=5,
    )
    assert result == []


def test_retrieve_empty_web_results():
    result = retrieve_combined_context(
        query="test query",
        pdf_vectorstore=None,
        web_results=[],
        top_k=5,
    )
    assert result == []


def test_retrieve_web_results_no_text():
    result = retrieve_combined_context(
        query="test",
        web_results=[{"type": "web", "title": "A", "url": "https://a.com", "text": ""}],
        top_k=5,
    )
    assert result == []


def test_retrieve_web_results_with_text():
    web_results = [
        {
            "type": "web",
            "title": "Article",
            "url": "https://example.com",
            "text": "This is a long article about Bangladesh budget policy and fiscal planning. " * 10,
            "source_name": "Web",
        }
    ]
    result = retrieve_combined_context(
        query="Bangladesh budget",
        web_results=web_results,
        top_k=3,
        use_pdf=False,
    )
    assert len(result) > 0
    assert result[0]["type"] == "web"


def test_summarize_empty_evidence():
    result = summarize_evidence("question?", [])
    assert "পাইনি" in result["answer"] or "যায়নি" in result["answer"]
    assert result["citations"] == []


def test_podcast_empty_evidence():
    result = create_podcast_script("topic", [])
    assert "পাওয়া যায়নি" in result["answer"] or "যায়নি" in result["answer"]
    assert result["citations"] == []


def test_no_evidence_message_constant():
    assert "নির্ভরযোগ্য" in NO_EVIDENCE_MSG or "সূত্র" in NO_EVIDENCE_MSG


def test_retrieve_both_disabled():
    result = retrieve_combined_context(
        query="test",
        pdf_vectorstore={"index": None, "chunks": []},
        web_results=[{"type": "web", "text": "content", "title": "T", "url": "u"}],
        use_pdf=False,
        use_web=False,
    )
    assert result == []
