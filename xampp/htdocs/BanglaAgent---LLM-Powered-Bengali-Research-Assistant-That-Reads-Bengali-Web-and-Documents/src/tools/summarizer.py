import logging
from src.llm import generate_summary
from src.utils.citations import sources_to_context_block, build_citation_string

logger = logging.getLogger(__name__)


def summarize_evidence(
    question: str,
    evidence: list[dict],
    language: str = "Bengali",
) -> dict:
    if not evidence:
        return {
            "answer": (
                "আমি নির্ভরযোগ্য সূত্রে এই তথ্যটি পাইনি। "
                "অনুগ্রহ করে আরেকটি সূত্র বা PDF দিন।"
            ),
            "citations": [],
            "limitations": "কোনো প্রমাণ পাওয়া যায়নি।",
        }

    context_block = sources_to_context_block(evidence)
    citation_string = build_citation_string(evidence)

    answer = generate_summary(
        context=context_block,
        question=question,
        language=language,
    )

    return {
        "answer": answer,
        "citations": [
            _extract_citation(e) for e in evidence
        ],
        "limitations": _assess_limitations(evidence),
    }


def _extract_citation(evidence_item: dict) -> str:
    from src.utils.citations import format_pdf_citation, format_web_citation
    if evidence_item.get("type") == "pdf":
        return format_pdf_citation(
            evidence_item.get("filename", "unknown.pdf"),
            evidence_item.get("page", 0),
        )
    elif evidence_item.get("type") == "web":
        return format_web_citation(
            evidence_item.get("title", ""),
            evidence_item.get("url", ""),
        )
    return ""


def _assess_limitations(evidence: list[dict]) -> str:
    pdf_count = sum(1 for e in evidence if e.get("type") == "pdf")
    web_count = sum(1 for e in evidence if e.get("type") == "web")
    limitations = []

    if pdf_count == 0 and web_count == 0:
        return "কোনো সূত্র পাওয়া যায়নি।"

    if pdf_count == 0:
        limitations.append("কোনো PDF সূত্র ব্যবহৃত হয়নি।")
    if web_count == 0:
        limitations.append("কোনো ওয়েব সূত্র ব্যবহৃত হয়নি।")
    if len(evidence) < 3:
        limitations.append("সীমিত সংখ্যক সূত্র পাওয়া গেছে।")

    return " ".join(limitations) if limitations else "পর্যাপ্ত সূত্র পাওয়া গেছে।"
