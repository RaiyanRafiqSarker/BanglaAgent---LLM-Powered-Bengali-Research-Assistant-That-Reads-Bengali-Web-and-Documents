import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def format_pdf_citation(filename: str, page: int) -> str:
    return f"[PDF: {filename}, page {page}]"


def format_web_citation(title: str, url: str) -> str:
    title = title.strip() if title else "Unknown"
    return f"[Source: {title}, {url}]"


def validate_citations(answer: str, sources: list[dict]) -> dict:
    source_keys = set()
    for s in sources:
        if s.get("type") == "pdf":
            source_keys.add(format_pdf_citation(
                s.get("filename", "unknown.pdf"), s.get("page", 0)
            ))
        elif s.get("type") == "web":
            source_keys.add(format_web_citation(
                s.get("title", ""), s.get("url", "")
            ))

    cited_in_answer = []
    uncited = []
    for key in source_keys:
        if key in answer:
            cited_in_answer.append(key)
        else:
            uncited.append(key)

    return {
        "cited": cited_in_answer,
        "uncited": uncited,
        "total_sources": len(sources),
        "citation_coverage": len(cited_in_answer) / max(len(source_keys), 1),
    }


def validate_and_fix_citations(answer: str, evidence: list[dict]) -> str:
    if not evidence or not answer:
        return answer

    valid_citations = set()
    for e in evidence:
        if e.get("type") == "pdf":
            valid_citations.add(format_pdf_citation(
                e.get("filename", "unknown.pdf"), e.get("page", 0)
            ))
        elif e.get("type") == "web":
            valid_citations.add(format_web_citation(
                e.get("title", ""), e.get("url", "")
            ))

    phantom_pdf = re.findall(r'\[PDF: [^\]]+\]', answer)
    phantom_web = re.findall(r'\[Source: [^\]]+\]', answer)
    all_cited = phantom_pdf + phantom_web

    for citation in all_cited:
        if citation not in valid_citations:
            logger.warning(f"[Citations] Removing phantom citation: {citation}")
            answer = answer.replace(citation, "")

    answer = re.sub(r'  +', ' ', answer)

    has_any_citation = any(c in answer for c in valid_citations)
    if not has_any_citation and evidence:
        source_section = "\n\n## সূত্র\n"
        for i, e in enumerate(evidence, 1):
            if e.get("type") == "pdf":
                c = format_pdf_citation(e.get("filename", ""), e.get("page", 0))
            elif e.get("type") == "web":
                c = format_web_citation(e.get("title", ""), e.get("url", ""))
            else:
                continue
            source_section += f"{i}. {c}\n"

        if "## সূত্র" not in answer:
            answer += source_section

    return answer


def deduplicate_sources(sources: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for s in sources:
        if s.get("type") == "pdf":
            key = (s.get("filename", ""), s.get("page", 0))
        elif s.get("type") == "web":
            key = s.get("url", "")
        else:
            key = s.get("text", "")[:100]

        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def build_citation_string(sources: list[dict]) -> str:
    citations = []
    for s in deduplicate_sources(sources):
        if s.get("type") == "pdf":
            citations.append(format_pdf_citation(
                s.get("filename", "unknown.pdf"), s.get("page", 0)
            ))
        elif s.get("type") == "web":
            citations.append(format_web_citation(
                s.get("title", ""), s.get("url", "")
            ))
    return '\n'.join(f"{i+1}. {c}" for i, c in enumerate(citations))


def sources_to_context_block(sources: list[dict]) -> str:
    blocks = []
    for i, s in enumerate(sources, 1):
        citation = ""
        if s.get("type") == "pdf":
            citation = format_pdf_citation(
                s.get("filename", "unknown.pdf"), s.get("page", 0)
            )
        elif s.get("type") == "web":
            citation = format_web_citation(
                s.get("title", ""), s.get("url", "")
            )

        text = s.get("text", "").strip()
        blocks.append(f"--- Evidence {i} {citation} ---\n{text}")
    return '\n\n'.join(blocks)
