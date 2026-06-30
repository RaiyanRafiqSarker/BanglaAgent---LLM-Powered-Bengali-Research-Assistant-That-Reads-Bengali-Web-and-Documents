import logging
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from config import UPLOAD_DIR, MAX_PDF_PAGES, FALLBACK_PDF_UNREADABLE
from src.utils.bengali_text import clean_bengali_text

logger = logging.getLogger(__name__)


def save_uploaded_pdf(file_path: str) -> str:
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not src.suffix.lower() == ".pdf":
        raise ValueError(f"Not a PDF file: {file_path}")

    upload_path = Path(UPLOAD_DIR) / src.name
    if str(src) != str(upload_path):
        import shutil
        shutil.copy2(str(src), str(upload_path))
    return str(upload_path)


def extract_pdf_text(file_path: str) -> list[dict]:
    pages = []
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Cannot open PDF {file_path}: {e}")
        raise ValueError(f"PDF ফাইলটি খোলা যায়নি: {e}")

    filename = Path(file_path).name
    total_pages = min(len(doc), MAX_PDF_PAGES)

    if total_pages == 0:
        doc.close()
        raise ValueError("PDF ফাইলটি খালি — কোনো পৃষ্ঠা নেই।")

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        text = clean_bengali_text(text)

        if text.strip():
            pages.append({
                "page": page_num + 1,
                "text": text,
                "filename": filename,
            })

    doc.close()

    if not pages:
        logger.warning(f"No text extracted from {filename} — may be image-based PDF")
        raise ValueError(FALLBACK_PDF_UNREADABLE)

    logger.info(f"Extracted {len(pages)} pages with text from {filename} (total: {total_pages})")
    return pages


def chunk_pdf_text(pages: list[dict]) -> list[dict]:
    from src.utils.chunking import chunk_pages
    return chunk_pages(pages)


def build_pdf_vectorstore(chunks: list[dict]) -> Optional[dict]:
    if not chunks:
        logger.warning("No chunks to build vectorstore from")
        return None

    import numpy as np
    import faiss
    from src.llm import create_embeddings

    texts = [c["text"] for c in chunks]

    try:
        embeddings = create_embeddings(texts)
    except Exception as e:
        logger.error(f"Embedding creation failed: {e}")
        raise ValueError(f"এমবেডিং তৈরি করতে ব্যর্থ: {e}")

    if not embeddings:
        logger.warning("Empty embeddings returned")
        return None

    dimension = len(embeddings[0])
    index = faiss.IndexFlatIP(dimension)

    vectors = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)
    index.add(vectors)

    logger.info(f"Built FAISS index with {len(chunks)} vectors (dim={dimension})")
    return {"index": index, "chunks": chunks}


def retrieve_pdf_context(
    query: str,
    vectorstore: dict,
    top_k: int = 5,
) -> list[dict]:
    if not vectorstore:
        return []

    import numpy as np
    import faiss
    from src.llm import create_embeddings

    index = vectorstore["index"]
    chunks = vectorstore["chunks"]

    if not chunks:
        return []

    try:
        query_embedding = create_embeddings([query])
    except Exception as e:
        logger.error(f"Query embedding failed: {e}")
        return []

    if not query_embedding:
        return []

    query_vec = np.array(query_embedding, dtype=np.float32)
    faiss.normalize_L2(query_vec)

    k = min(top_k, len(chunks))
    scores, indices = index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        fn = chunk["metadata"].get("filename", "unknown.pdf")
        pg = chunk["metadata"].get("page", 0)
        results.append({
            "text": chunk["text"],
            "type": "pdf",
            "filename": fn,
            "page": pg,
            "score": float(score),
            "citation": f"[PDF: {fn}, page {pg}]",
            "source_type": "pdf",
            "evidence_strength": "strong",
        })

    logger.info(f"PDF retrieval returned {len(results)} chunks for query: {query[:60]}")
    return results
