from typing import Optional
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    metadata: Optional[dict] = None,
) -> list[dict]:
    if not text or not text.strip():
        return []

    metadata = metadata or {}
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end < text_len:
            for sep in ['\n\n', '\n', '। ', '. ', ' ']:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start:
                    end = last_sep + len(sep)
                    break

        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunk_meta = {**metadata, "chunk_index": len(chunks)}
            chunks.append({"text": chunk_text_str, "metadata": chunk_meta})

        start = end - chunk_overlap
        if start <= (end - chunk_size):
            start = end

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    all_chunks = []
    for page in pages:
        page_text = page.get("text", "")
        page_num = page.get("page", 0)
        filename = page.get("filename", "unknown.pdf")

        page_chunks = chunk_text(
            page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata={
                "type": "pdf",
                "page": page_num,
                "filename": filename,
            },
        )
        all_chunks.extend(page_chunks)
    return all_chunks


def merge_small_chunks(chunks: list[dict], min_size: int = 100) -> list[dict]:
    if not chunks:
        return []

    merged = []
    buffer = None

    for chunk in chunks:
        if buffer is None:
            buffer = chunk.copy()
            continue

        if len(buffer["text"]) < min_size:
            buffer["text"] = buffer["text"] + "\n" + chunk["text"]
        else:
            merged.append(buffer)
            buffer = chunk.copy()

    if buffer:
        merged.append(buffer)

    return merged
