import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import BanglaAgent, is_pdf_specific_query
from config import FALLBACK_NO_EVIDENCE, FALLBACK_NO_PDF_EVIDENCE


def test_empty_question():
    agent = BanglaAgent()
    result = agent.run(question="")
    assert "প্রশ্ন" in result["answer"]
    assert result["citations"] == []
    assert result["evidence"] == []


def test_no_pdf_sets_use_pdf_false():
    agent = BanglaAgent()
    with patch("src.agent.search_bengali_web", return_value=[]):
        result = agent.run(
            question="test query",
            pdf_file=None,
            use_web=True,
            use_pdf=True,
        )
    assert FALLBACK_NO_EVIDENCE in result["answer"] or "পাইনি" in result["answer"]


def test_pdf_specific_no_evidence_returns_pdf_fallback():
    agent = BanglaAgent()
    with patch("src.agent.search_bengali_web", return_value=[]):
        result = agent.run(
            question="এই PDF অনুযায়ী বাজেটের তথ্য দাও",
            pdf_file=None,
            use_web=False,
            use_pdf=True,
        )
    assert result["evidence"] == []


def test_both_disabled_enables_web():
    agent = BanglaAgent()
    with patch("src.agent.search_bengali_web", return_value=[]) as mock_search:
        result = agent.run(
            question="some question",
            pdf_file=None,
            use_web=False,
            use_pdf=False,
        )
    mock_search.assert_called_once()


def test_pdf_specific_skips_web_search():
    agent = BanglaAgent()
    agent._pdf_vectorstore = {"index": MagicMock(), "chunks": []}
    agent._pdf_filename = "test.pdf"

    with patch("src.agent.search_bengali_web") as mock_search, \
         patch("src.agent.retrieve_combined_context", return_value=[]):
        agent.run(
            question="এই PDF থেকে মূল তথ্য দাও",
            pdf_file=None,
            use_web=True,
            use_pdf=True,
        )
    mock_search.assert_not_called()


def test_pdf_specific_with_web_explicit_searches_web():
    agent = BanglaAgent()
    agent._pdf_vectorstore = {"index": MagicMock(), "chunks": []}
    agent._pdf_filename = "test.pdf"

    with patch("src.agent.search_bengali_web", return_value=[]) as mock_search, \
         patch("src.agent.retrieve_combined_context", return_value=[]):
        agent.run(
            question="এই PDF-এর সাথে সাম্প্রতিক ওয়েব তথ্য তুলনা করো",
            pdf_file=None,
            use_web=True,
            use_pdf=True,
        )
    mock_search.assert_called_once()
