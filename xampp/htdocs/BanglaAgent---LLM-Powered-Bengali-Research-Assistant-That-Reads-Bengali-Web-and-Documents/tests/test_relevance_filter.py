import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.retriever import (
    compute_lexical_overlap,
    filter_by_relevance,
    retrieve_combined_context,
)


def test_lexical_overlap_high():
    query = "বাংলাদেশ বাজেট অগ্রাধিকার"
    text = "বাংলাদেশ সরকারের বাজেটে প্রধান অগ্রাধিকার হলো শিক্ষা ও স্বাস্থ্য খাত।"
    overlap = compute_lexical_overlap(query, text)
    assert overlap > 0.3


def test_lexical_overlap_zero():
    query = "বাংলাদেশ বাজেট অগ্রাধিকার"
    text = "পঞ্চম শ্রেণির বাংলা বই থেকে গল্প পড়ুন"
    overlap = compute_lexical_overlap(query, text)
    assert overlap < 0.5


def test_filter_rejects_irrelevant_web():
    evidence = [
        {
            "text": "পঞ্চম শ্রেণির বাংলা বই এর পাঠ্যসূচি নতুন করে সাজানো হয়েছে।",
            "type": "web",
            "score": 0.05,
            "title": "Class Five Bengali Textbook",
            "url": "https://example.com/class5",
        },
    ]
    query = "বাংলাদেশ বাজেটের প্রধান অগ্রাধিকার"
    accepted, rejected = filter_by_relevance(evidence, query)
    assert rejected >= 1
    assert len(accepted) == 0


def test_filter_accepts_relevant_pdf():
    evidence = [
        {
            "text": "২০২৪-২৫ অর্থবছরের বাজেটে শিক্ষা খাতে বরাদ্দ বৃদ্ধি করা হয়েছে।",
            "type": "pdf",
            "score": 0.6,
            "filename": "budget.pdf",
            "page": 1,
        },
    ]
    query = "বাজেটে শিক্ষা খাতে বরাদ্দ"
    accepted, rejected = filter_by_relevance(evidence, query)
    assert len(accepted) == 1
    assert rejected == 0


def test_filter_accepts_relevant_web():
    evidence = [
        {
            "text": "বাংলাদেশের ২০২৪ সালের বাজেটে স্বাস্থ্য খাতে বরাদ্দ বাড়ানো হয়েছে।",
            "type": "web",
            "score": 0.4,
            "title": "Budget News",
            "url": "https://example.com/budget",
        },
    ]
    query = "বাংলাদেশ বাজেট স্বাস্থ্য বরাদ্দ"
    accepted, rejected = filter_by_relevance(evidence, query)
    assert len(accepted) == 1


def test_retrieve_with_pdf_specific():
    web_results = [
        {
            "type": "web",
            "title": "Unrelated Article",
            "url": "https://example.com/unrelated",
            "text": "This is completely unrelated content about something else entirely. " * 5,
            "source_name": "Web",
        }
    ]
    result = retrieve_combined_context(
        query="এই PDF অনুযায়ী বাজেটের তথ্য",
        pdf_vectorstore=None,
        web_results=web_results,
        top_k=5,
        use_pdf=False,
        use_web=True,
        pdf_specific=True,
    )
    assert len(result) == 0


def test_retrieve_empty_returns_empty():
    result = retrieve_combined_context(
        query="test",
        pdf_vectorstore=None,
        web_results=None,
        top_k=5,
    )
    assert result == []
