import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.citations import validate_and_fix_citations, validate_citations


def test_phantom_citation_removed():
    evidence = [
        {"type": "pdf", "filename": "budget.pdf", "page": 1, "text": "content"},
    ]
    answer = (
        "The answer is here [PDF: budget.pdf, page 1] "
        "and also [PDF: nonexistent.pdf, page 99]."
    )
    fixed = validate_and_fix_citations(answer, evidence)
    assert "[PDF: budget.pdf, page 1]" in fixed
    assert "[PDF: nonexistent.pdf, page 99]" not in fixed


def test_web_phantom_citation_removed():
    evidence = [
        {"type": "web", "title": "Real Article", "url": "https://real.com", "text": "content"},
    ]
    answer = (
        "Answer [Source: Real Article, https://real.com] "
        "[Source: Fake Article, https://fake.com]"
    )
    fixed = validate_and_fix_citations(answer, evidence)
    assert "[Source: Real Article, https://real.com]" in fixed
    assert "[Source: Fake Article, https://fake.com]" not in fixed


def test_source_section_appended_when_no_citations():
    evidence = [
        {"type": "pdf", "filename": "doc.pdf", "page": 3, "text": "content"},
    ]
    answer = "This answer has no inline citations at all."
    fixed = validate_and_fix_citations(answer, evidence)
    assert "## সূত্র" in fixed
    assert "doc.pdf" in fixed


def test_empty_evidence_no_change():
    answer = "Some answer."
    fixed = validate_and_fix_citations(answer, [])
    assert fixed == answer


def test_empty_answer_no_change():
    fixed = validate_and_fix_citations("", [{"type": "pdf", "filename": "a.pdf", "page": 1}])
    assert fixed == ""


def test_valid_citations_untouched():
    evidence = [
        {"type": "pdf", "filename": "budget.pdf", "page": 1, "text": "content"},
        {"type": "pdf", "filename": "budget.pdf", "page": 2, "text": "more content"},
    ]
    answer = (
        "Point one [PDF: budget.pdf, page 1]. "
        "Point two [PDF: budget.pdf, page 2]."
    )
    fixed = validate_and_fix_citations(answer, evidence)
    assert "[PDF: budget.pdf, page 1]" in fixed
    assert "[PDF: budget.pdf, page 2]" in fixed
