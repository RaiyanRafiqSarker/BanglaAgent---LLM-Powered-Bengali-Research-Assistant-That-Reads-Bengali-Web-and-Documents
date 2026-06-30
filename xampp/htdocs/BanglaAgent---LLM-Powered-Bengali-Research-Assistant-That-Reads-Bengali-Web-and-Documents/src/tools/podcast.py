import logging
from src.llm import generate_podcast_script
from src.utils.citations import sources_to_context_block, build_citation_string

logger = logging.getLogger(__name__)


def create_podcast_script(
    question: str,
    evidence: list[dict],
    language: str = "Bengali",
) -> dict:
    if not evidence:
        return {
            "answer": (
                "পডকাস্ট স্ক্রিপ্ট তৈরি করা যায়নি কারণ কোনো প্রমাণ পাওয়া যায়নি। "
                "অনুগ্রহ করে একটি PDF আপলোড করুন বা ওয়েব সার্চ সক্রিয় করুন।"
            ),
            "citations": [],
            "limitations": "কোনো প্রমাণ পাওয়া যায়নি।",
        }

    context_block = sources_to_context_block(evidence)
    citation_string = build_citation_string(evidence)

    script = generate_podcast_script(
        context=context_block,
        question=question,
        language=language,
    )

    citations = []
    for e in evidence:
        from src.utils.citations import format_pdf_citation, format_web_citation
        if e.get("type") == "pdf":
            citations.append(format_pdf_citation(e.get("filename", ""), e.get("page", 0)))
        elif e.get("type") == "web":
            citations.append(format_web_citation(e.get("title", ""), e.get("url", "")))

    return {
        "answer": script,
        "citations": citations,
        "limitations": _podcast_limitations(evidence),
    }


def _podcast_limitations(evidence: list[dict]) -> str:
    if len(evidence) < 2:
        return "সীমিত সূত্রের উপর ভিত্তি করে স্ক্রিপ্ট তৈরি হয়েছে।"
    return "উপলব্ধ সূত্রের ভিত্তিতে স্ক্রিপ্ট তৈরি হয়েছে।"
