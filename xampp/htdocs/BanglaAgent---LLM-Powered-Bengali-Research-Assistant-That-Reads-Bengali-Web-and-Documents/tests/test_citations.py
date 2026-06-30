import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.citations import (
    format_pdf_citation,
    format_web_citation,
    validate_citations,
    deduplicate_sources,
    build_citation_string,
    sources_to_context_block,
)


def test_format_pdf_citation():
    c = format_pdf_citation("budget.pdf", 12)
    assert c == "[PDF: budget.pdf, page 12]"


def test_format_pdf_citation_page_zero():
    c = format_pdf_citation("doc.pdf", 0)
    assert "page 0" in c


def test_format_web_citation():
    c = format_web_citation("Bangladesh Budget 2024", "https://example.com/article")
    assert c == "[Source: Bangladesh Budget 2024, https://example.com/article]"


def test_format_web_citation_empty_title():
    c = format_web_citation("", "https://example.com")
    assert "Unknown" in c


def test_validate_citations_all_cited():
    sources = [
        {"type": "pdf", "filename": "doc.pdf", "page": 1},
        {"type": "web", "title": "Article", "url": "https://example.com"},
    ]
    answer = (
        "Some answer [PDF: doc.pdf, page 1] and "
        "[Source: Article, https://example.com]"
    )
    result = validate_citations(answer, sources)
    assert result["citation_coverage"] == 1.0
    assert len(result["cited"]) == 2
    assert len(result["uncited"]) == 0


def test_validate_citations_none_cited():
    sources = [{"type": "pdf", "filename": "doc.pdf", "page": 5}]
    answer = "Some answer without citations."
    result = validate_citations(answer, sources)
    assert result["citation_coverage"] == 0.0
    assert len(result["uncited"]) == 1


def test_validate_citations_empty():
    result = validate_citations("answer", [])
    assert result["total_sources"] == 0
    assert result["citation_coverage"] == 0.0


def test_deduplicate_sources_pdf():
    sources = [
        {"type": "pdf", "filename": "a.pdf", "page": 1, "text": "hello"},
        {"type": "pdf", "filename": "a.pdf", "page": 1, "text": "hello duplicate"},
        {"type": "pdf", "filename": "a.pdf", "page": 2, "text": "different"},
    ]
    unique = deduplicate_sources(sources)
    assert len(unique) == 2


def test_deduplicate_sources_web():
    sources = [
        {"type": "web", "url": "https://example.com/1", "title": "A", "text": "..."},
        {"type": "web", "url": "https://example.com/1", "title": "A dup", "text": "..."},
        {"type": "web", "url": "https://example.com/2", "title": "B", "text": "..."},
    ]
    unique = deduplicate_sources(sources)
    assert len(unique) == 2


def test_deduplicate_sources_mixed():
    sources = [
        {"type": "pdf", "filename": "a.pdf", "page": 1, "text": "pdf"},
        {"type": "web", "url": "https://example.com", "title": "Web", "text": "web"},
    ]
    unique = deduplicate_sources(sources)
    assert len(unique) == 2


def test_deduplicate_empty():
    assert deduplicate_sources([]) == []


def test_build_citation_string():
    sources = [
        {"type": "pdf", "filename": "budget.pdf", "page": 3},
        {"type": "web", "title": "News", "url": "https://news.com"},
    ]
    result = build_citation_string(sources)
    assert "budget.pdf" in result
    assert "News" in result
    assert "1." in result
    assert "2." in result


def test_sources_to_context_block():
    sources = [
        {"type": "pdf", "filename": "doc.pdf", "page": 1, "text": "PDF content here"},
        {"type": "web", "title": "Article", "url": "https://ex.com", "text": "Web content"},
    ]
    block = sources_to_context_block(sources)
    assert "Evidence 1" in block
    assert "Evidence 2" in block
    assert "PDF content here" in block
    assert "Web content" in block
