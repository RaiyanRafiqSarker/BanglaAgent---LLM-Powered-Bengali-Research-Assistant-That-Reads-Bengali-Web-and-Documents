import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.pdf_reader import save_uploaded_pdf, extract_pdf_text, chunk_pdf_text
from src.utils.chunking import chunk_pages
import pytest


def _create_test_pdf(text_pages: list[str]) -> str:
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not installed")

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc = fitz.open()
    for text in text_pages:
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=12)
    doc.save(tmp.name)
    doc.close()
    tmp.close()
    return tmp.name


def test_extract_single_page_pdf():
    pdf_path = _create_test_pdf(["This is page one content about budget allocation."])
    pages = extract_pdf_text(pdf_path)
    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert "budget" in pages[0]["text"].lower()
    assert pages[0]["filename"].endswith(".pdf")
    Path(pdf_path).unlink(missing_ok=True)


def test_extract_multi_page_pdf():
    pdf_path = _create_test_pdf([
        "Page one about education spending.",
        "Page two about healthcare budget.",
        "Page three about infrastructure investment.",
    ])
    pages = extract_pdf_text(pdf_path)
    assert len(pages) == 3
    assert pages[0]["page"] == 1
    assert pages[1]["page"] == 2
    assert pages[2]["page"] == 3
    Path(pdf_path).unlink(missing_ok=True)


def test_extract_empty_pdf():
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not installed")

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc = fitz.open()
    doc.new_page()
    doc.save(tmp.name)
    doc.close()
    tmp.close()

    with pytest.raises(ValueError, match="টেক্সট"):
        extract_pdf_text(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


def test_chunk_pdf_pages():
    pages = [
        {"text": "Budget allocation details. " * 50, "page": 1, "filename": "test.pdf"},
        {"text": "Healthcare spending overview. " * 50, "page": 2, "filename": "test.pdf"},
    ]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 2
    for c in chunks:
        assert c["metadata"]["filename"] == "test.pdf"
        assert c["metadata"]["page"] in [1, 2]


def test_save_uploaded_pdf():
    pdf_path = _create_test_pdf(["Test content"])
    saved = save_uploaded_pdf(pdf_path)
    assert Path(saved).exists()
    Path(pdf_path).unlink(missing_ok=True)
    Path(saved).unlink(missing_ok=True)


def test_save_nonexistent_pdf_raises():
    with pytest.raises(FileNotFoundError):
        save_uploaded_pdf("/nonexistent/fake.pdf")


def test_save_non_pdf_raises():
    tmp = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    tmp.write(b"not a pdf")
    tmp.close()
    with pytest.raises(ValueError, match="Not a PDF"):
        save_uploaded_pdf(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)
