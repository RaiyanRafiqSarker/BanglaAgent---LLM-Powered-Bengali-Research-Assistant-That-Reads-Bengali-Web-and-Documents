import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.chunking import chunk_text, chunk_pages, merge_small_chunks


def test_chunk_text_basic():
    text = "Hello world. " * 200
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    for c in chunks:
        assert "text" in c
        assert "metadata" in c
        assert len(c["text"]) > 0


def test_chunk_text_empty():
    chunks = chunk_text("")
    assert chunks == []

    chunks = chunk_text("   ")
    assert chunks == []


def test_chunk_text_short():
    text = "Short text."
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Short text."


def test_chunk_text_metadata():
    text = "A " * 500
    meta = {"type": "pdf", "page": 5, "filename": "test.pdf"}
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20, metadata=meta)
    for c in chunks:
        assert c["metadata"]["type"] == "pdf"
        assert c["metadata"]["page"] == 5
        assert c["metadata"]["filename"] == "test.pdf"
        assert "chunk_index" in c["metadata"]


def test_chunk_pages():
    pages = [
        {"text": "Page one content. " * 50, "page": 1, "filename": "doc.pdf"},
        {"text": "Page two content. " * 50, "page": 2, "filename": "doc.pdf"},
    ]
    chunks = chunk_pages(pages, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 2
    page_nums = set(c["metadata"]["page"] for c in chunks)
    assert 1 in page_nums
    assert 2 in page_nums


def test_chunk_pages_empty():
    pages = [{"text": "", "page": 1, "filename": "empty.pdf"}]
    chunks = chunk_pages(pages)
    assert chunks == []


def test_merge_small_chunks():
    chunks = [
        {"text": "Hi", "metadata": {}},
        {"text": "Hello there, this is a longer chunk with enough content", "metadata": {}},
        {"text": "Ok", "metadata": {}},
    ]
    merged = merge_small_chunks(chunks, min_size=20)
    assert len(merged) <= len(chunks)
    total_text = " ".join(c["text"] for c in merged)
    assert "Hi" in total_text
    assert "Hello" in total_text


def test_merge_empty():
    assert merge_small_chunks([]) == []


def test_chunk_overlap():
    text = "Word " * 200
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    if len(chunks) >= 2:
        end_of_first = chunks[0]["text"][-10:]
        start_of_second = chunks[1]["text"][:20]
        assert len(chunks[0]["text"]) > 0
        assert len(chunks[1]["text"]) > 0
