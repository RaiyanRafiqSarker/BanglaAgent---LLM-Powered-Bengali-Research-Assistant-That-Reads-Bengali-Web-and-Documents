import logging
from typing import Optional
from pathlib import Path

from src.llm import generate_answer
from src.tools.web_search import search_bengali_web
from src.tools.pdf_reader import (
    save_uploaded_pdf,
    extract_pdf_text,
    chunk_pdf_text,
    build_pdf_vectorstore,
    retrieve_pdf_context,
)
from src.tools.retriever import retrieve_combined_context
from src.tools.summarizer import summarize_evidence
from src.tools.podcast import create_podcast_script
from src.utils.citations import (
    sources_to_context_block,
    build_citation_string,
    deduplicate_sources,
    validate_and_fix_citations,
)
from config import (
    PDF_SPECIFIC_PATTERNS,
    WEB_EXPLICIT_PATTERNS,
    FALLBACK_NO_PDF_EVIDENCE,
    FALLBACK_NO_EVIDENCE,
)

logger = logging.getLogger(__name__)


def is_pdf_specific_query(question: str) -> bool:
    q_lower = question.lower()
    for pattern in PDF_SPECIFIC_PATTERNS:
        if pattern.lower() in q_lower:
            return True
    return False


def is_web_explicit_query(question: str) -> bool:
    q_lower = question.lower()
    for pattern in WEB_EXPLICIT_PATTERNS:
        if pattern.lower() in q_lower:
            return True
    return False


class BanglaAgent:
    def __init__(self):
        self._pdf_vectorstore: Optional[dict] = None
        self._pdf_filename: Optional[str] = None
        self._status_callback = None

    def set_status_callback(self, callback):
        self._status_callback = callback

    def _update_status(self, message: str):
        if self._status_callback:
            self._status_callback(message)
        logger.info(message)

    def process_pdf(self, file_path: str) -> str:
        self._update_status("PDF reading...")
        try:
            saved_path = save_uploaded_pdf(file_path)
            pages = extract_pdf_text(saved_path)

            if not pages:
                return "PDF could not extract text — may be image-based."

            self._update_status("Building vector embeddings...")
            chunks = chunk_pdf_text(pages)
            self._pdf_vectorstore = build_pdf_vectorstore(chunks)
            self._pdf_filename = Path(saved_path).name

            page_count = len(pages)
            chunk_count = len(chunks)
            logger.info(
                f"[BanglaAgent] PDF processed: {self._pdf_filename}, "
                f"pages={page_count}, chunks={chunk_count}"
            )
            return (
                f"PDF processed: {self._pdf_filename}, "
                f"{page_count} pages, {chunk_count} chunks"
            )
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            self._pdf_vectorstore = None
            self._pdf_filename = None
            return f"PDF processing error: {e}"

    def clear_session(self):
        self._pdf_vectorstore = None
        self._pdf_filename = None

    def run(
        self,
        question: str,
        pdf_file: Optional[str] = None,
        use_web: bool = True,
        use_pdf: bool = True,
        mode: str = "Detailed Research Answer",
        top_k: int = 5,
        answer_language: str = "Bengali",
        podcast_format: bool = False,
    ) -> dict:
        logger.info(f"[BanglaAgent] question={question!r}")
        logger.info(f"[BanglaAgent] pdf_file={'set' if pdf_file else 'None'}")
        logger.info(f"[BanglaAgent] use_pdf={use_pdf}, use_web={use_web}")
        logger.info(f"[BanglaAgent] mode={mode}, top_k={top_k}, language={answer_language}")

        if not question or not question.strip():
            return {
                "answer": "অনুগ্রহ করে একটি প্রশ্ন লিখুন।",
                "citations": [],
                "evidence": [],
                "limitations": "",
            }

        if pdf_file is None:
            use_pdf = False

        pdf_specific = is_pdf_specific_query(question)
        web_explicit = is_web_explicit_query(question)
        logger.info(f"[BanglaAgent] pdf_specific_query={pdf_specific}")
        logger.info(f"[BanglaAgent] web_explicit_query={web_explicit}")

        if not use_web and not use_pdf:
            use_web = True

        if pdf_file and use_pdf:
            pdf_status = self.process_pdf(pdf_file)
            if "error" in pdf_status.lower() or "could not" in pdf_status.lower():
                logger.warning(f"[BanglaAgent] PDF issue: {pdf_status}")
                if pdf_specific and not use_web:
                    return {
                        "answer": FALLBACK_NO_PDF_EVIDENCE,
                        "citations": [],
                        "evidence": [],
                        "limitations": pdf_status,
                    }

        should_search_web = False
        if use_web:
            if pdf_specific and self._pdf_vectorstore:
                if web_explicit:
                    should_search_web = True
                    logger.info("[BanglaAgent] PDF-specific + web-explicit → searching web too")
                else:
                    should_search_web = False
                    logger.info("[BanglaAgent] PDF-specific query → skipping web search")
            else:
                should_search_web = True

        web_results = []
        if should_search_web:
            self._update_status("Searching web...")
            try:
                web_results = search_bengali_web(question, max_results=top_k)
            except Exception as e:
                logger.warning(f"[BanglaAgent] Web search failed: {e}")
                web_results = []

        logger.info(f"[BanglaAgent] web_results_count={len(web_results)}")
        logger.info(f"[BanglaAgent] pdf_vectorstore={'loaded' if self._pdf_vectorstore else 'None'}")

        self._update_status("Retrieving relevant evidence...")
        evidence = retrieve_combined_context(
            query=question,
            pdf_vectorstore=self._pdf_vectorstore if use_pdf else None,
            web_results=web_results if should_search_web else None,
            top_k=top_k,
            use_pdf=use_pdf,
            use_web=should_search_web,
            pdf_specific=pdf_specific and use_pdf and self._pdf_vectorstore is not None,
        )

        web_count = sum(1 for e in evidence if e.get("type") == "web")
        pdf_count = sum(1 for e in evidence if e.get("type") == "pdf")
        logger.info(f"[BanglaAgent] pdf_evidence_count={pdf_count}")
        logger.info(f"[BanglaAgent] web_evidence_count={web_count}")
        logger.info(f"[BanglaAgent] final_evidence_count={len(evidence)}")

        if not evidence:
            if pdf_specific and use_pdf:
                fallback_msg = FALLBACK_NO_PDF_EVIDENCE
            else:
                fallback_msg = FALLBACK_NO_EVIDENCE
            return {
                "answer": fallback_msg,
                "citations": [],
                "evidence": [],
                "limitations": "কোনো প্রাসঙ্গিক সূত্র পাওয়া যায়নি।",
            }

        evidence_types = set(e.get("type") for e in evidence)
        is_pdf_only_evidence = evidence_types == {"pdf"}

        if mode == "Podcast Script" or podcast_format:
            self._update_status("Writing podcast script...")
            result = create_podcast_script(
                question=question,
                evidence=evidence,
                language=answer_language,
            )
        elif mode == "Quick Summary":
            self._update_status("Creating summary...")
            result = summarize_evidence(
                question=question,
                evidence=evidence,
                language=answer_language,
            )
        else:
            self._update_status("Generating answer...")
            context_block = sources_to_context_block(evidence)
            citation_string = build_citation_string(evidence)

            answer = generate_answer(
                prompt=question,
                context=context_block,
                sources=citation_string,
                language=answer_language,
                pdf_only=is_pdf_only_evidence,
            )

            answer = validate_and_fix_citations(answer, evidence)

            result = {
                "answer": answer,
                "citations": [self._format_single_citation(e) for e in evidence],
                "limitations": self._assess_overall_limitations(
                    evidence, use_web, use_pdf
                ),
            }

        result["evidence"] = evidence
        citations = [self._format_single_citation(e) for e in evidence]
        logger.info(f"[BanglaAgent] citations={citations}")
        return result

    def _format_single_citation(self, evidence_item: dict) -> str:
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

    def _assess_overall_limitations(
        self,
        evidence: list[dict],
        use_web: bool,
        use_pdf: bool,
    ) -> str:
        parts = []
        if not use_web:
            parts.append("ওয়েব সার্চ নিষ্ক্রিয় ছিল।")
        if not use_pdf:
            parts.append("PDF ব্যবহার নিষ্ক্রিয় ছিল।")
        if self._pdf_vectorstore is None and use_pdf:
            parts.append("কোনো PDF আপলোড করা হয়নি।")

        web_count = sum(1 for e in evidence if e.get("type") == "web")
        pdf_count = sum(1 for e in evidence if e.get("type") == "pdf")

        if web_count == 0 and use_web:
            parts.append("ওয়েব থেকে কোনো ফলাফল পাওয়া যায়নি।")
        if pdf_count == 0 and use_pdf and self._pdf_vectorstore:
            parts.append("PDF থেকে প্রাসঙ্গিক তথ্য পাওয়া যায়নি।")
        if len(evidence) < 3:
            parts.append("সীমিত সংখ্যক সূত্র পাওয়া গেছে — উত্তর সম্পূর্ণ নাও হতে পারে।")

        return " ".join(parts) if parts else "পর্যাপ্ত সূত্র ব্যবহৃত হয়েছে।"
