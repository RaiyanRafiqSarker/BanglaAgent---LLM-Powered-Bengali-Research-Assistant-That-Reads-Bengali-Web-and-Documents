import re
import logging
from typing import Optional
from src.utils.citations import deduplicate_sources
from config import MIN_RELEVANCE_SCORE, MIN_LEXICAL_OVERLAP, MAX_EVIDENCE_CHUNKS

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\sঀ-৿]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _extract_terms(text: str) -> set[str]:
    normalized = _normalize_text(text)
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to",
        "for", "of", "with", "and", "or", "but", "not", "this", "that",
        "এই", "সেই", "একটি", "করে", "করা", "হয়", "থেকে", "জন্য",
        "এবং", "বা", "না", "তা", "যা", "কি", "কী", "দিন", "দাও",
        "অনুযায়ী", "pdf", "ডকুমেন্ট",
    }
    terms = set(normalized.split())
    return terms - stop_words


def compute_lexical_overlap(query: str, text: str) -> float:
    query_terms = _extract_terms(query)
    text_terms = _extract_terms(text)
    if not query_terms:
        return 0.0
    overlap = query_terms & text_terms
    return len(overlap) / len(query_terms)


def filter_by_relevance(
    evidence: list[dict],
    query: str,
    min_score: float = MIN_RELEVANCE_SCORE,
    min_lexical: float = MIN_LEXICAL_OVERLAP,
) -> tuple[list[dict], int]:
    accepted = []
    rejected = 0

    for item in evidence:
        score = item.get("score", 0.0)
        text = item.get("text", "")
        lexical = compute_lexical_overlap(query, text)
        item["lexical_overlap"] = lexical

        if item.get("type") == "pdf":
            if score >= min_score * 0.5 or lexical >= min_lexical * 0.5:
                accepted.append(item)
            else:
                rejected += 1
                logger.info(
                    f"[Retriever] REJECTED PDF chunk (score={score:.3f}, lexical={lexical:.3f}): "
                    f"{text[:80]}"
                )
        else:
            if score >= min_score and lexical >= min_lexical:
                accepted.append(item)
            elif score >= min_score * 2:
                accepted.append(item)
            elif lexical >= min_lexical * 2:
                accepted.append(item)
            else:
                rejected += 1
                logger.info(
                    f"[Retriever] REJECTED web chunk (score={score:.3f}, lexical={lexical:.3f}): "
                    f"{text[:80]}"
                )

    return accepted, rejected


def retrieve_combined_context(
    query: str,
    pdf_vectorstore: Optional[dict] = None,
    web_results: Optional[list[dict]] = None,
    top_k: int = 5,
    use_pdf: bool = True,
    use_web: bool = True,
    pdf_specific: bool = False,
) -> list[dict]:
    all_evidence = []

    if use_pdf and pdf_vectorstore:
        from src.tools.pdf_reader import retrieve_pdf_context
        pdf_results = retrieve_pdf_context(query, pdf_vectorstore, top_k=top_k)
        all_evidence.extend(pdf_results)
        logger.info(f"[Retriever] Raw PDF evidence: {len(pdf_results)}")

    web_evidence = []
    if use_web and web_results:
        from src.utils.chunking import chunk_text
        for article in web_results:
            text = article.get("text", "")
            if not text.strip():
                continue

            article_chunks = chunk_text(
                text,
                chunk_size=600,
                chunk_overlap=100,
                metadata={
                    "type": "web",
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source_name": article.get("source_name", "Web"),
                },
            )

            evidence_strength = article.get("evidence_strength", "weak")
            for chunk in article_chunks:
                web_evidence.append({
                    "text": chunk["text"],
                    "type": "web",
                    "title": chunk["metadata"].get("title", ""),
                    "url": chunk["metadata"].get("url", ""),
                    "source_name": chunk["metadata"].get("source_name", "Web"),
                    "score": 0.0,
                    "evidence_strength": evidence_strength,
                    "source_type": "web",
                })

        logger.info(f"[Retriever] Raw web evidence chunks: {len(web_evidence)}")

    if web_evidence:
        web_evidence = _rank_web_evidence(query, web_evidence, top_k)
        all_evidence.extend(web_evidence)

    accepted, rejected = filter_by_relevance(all_evidence, query)
    logger.info(
        f"[Retriever] After relevance filter: accepted={len(accepted)}, rejected={rejected}"
    )

    if pdf_specific:
        pdf_evidence = [e for e in accepted if e.get("type") == "pdf"]
        web_accepted = [e for e in accepted if e.get("type") == "web"]

        if pdf_evidence:
            accepted = pdf_evidence
            logger.info(
                f"[Retriever] PDF-specific query: using {len(pdf_evidence)} PDF chunks, "
                f"dropped {len(web_accepted)} web chunks"
            )
        else:
            accepted = []
            logger.info("[Retriever] PDF-specific query but no PDF evidence passed filter")

    accepted = deduplicate_sources(accepted)

    accepted.sort(key=lambda x: x.get("score", 0), reverse=True)

    max_chunks = MAX_EVIDENCE_CHUNKS
    return accepted[:max_chunks]


def _rank_web_evidence(query: str, evidence: list[dict], top_k: int) -> list[dict]:
    query_terms = _extract_terms(query)

    for item in evidence:
        if item.get("type") != "web":
            continue
        text_terms = _extract_terms(item["text"])
        if not query_terms:
            item["score"] = 0.0
            continue
        overlap = query_terms & text_terms
        item["score"] = len(overlap) / len(query_terms)

    evidence.sort(key=lambda x: x.get("score", 0), reverse=True)
    return evidence
