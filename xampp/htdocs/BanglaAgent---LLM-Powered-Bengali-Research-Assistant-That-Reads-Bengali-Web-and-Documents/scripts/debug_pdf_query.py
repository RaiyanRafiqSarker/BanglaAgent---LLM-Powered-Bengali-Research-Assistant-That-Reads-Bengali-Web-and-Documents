#!/usr/bin/env python3
"""
Debug script: diagnose PDF retrieval without the UI.

Usage:
    python scripts/debug_pdf_query.py path/to/demo.pdf "এই PDF অনুযায়ী বাজেটের প্রধান অগ্রাধিকার কী?"
"""
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from dotenv import load_dotenv
load_dotenv()

from src.tools.pdf_reader import extract_pdf_text, chunk_pdf_text, build_pdf_vectorstore, retrieve_pdf_context
from src.tools.retriever import retrieve_combined_context, filter_by_relevance
from src.utils.citations import sources_to_context_block, build_citation_string
from src.llm import generate_answer
from src.agent import is_pdf_specific_query


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/debug_pdf_query.py <pdf_path> <question>")
        print('Example: python scripts/debug_pdf_query.py demo.pdf "এই PDF অনুযায়ী বাজেটের তথ্য দাও"')
        sys.exit(1)

    pdf_path = sys.argv[1]
    question = sys.argv[2]

    if not Path(pdf_path).exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        print("ERROR: OPENAI_API_KEY not set. Add to .env file.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"PDF: {pdf_path}")
    print(f"Question: {question}")
    print(f"PDF-specific: {is_pdf_specific_query(question)}")
    print(f"{'='*60}\n")

    print("--- Step 1: Extract PDF text ---")
    try:
        pages = extract_pdf_text(pdf_path)
        print(f"Extracted page count: {len(pages)}")
        if pages:
            first_text = pages[0]["text"][:500]
            print(f"First 500 chars of page 1:\n{first_text}\n")
    except Exception as e:
        print(f"ERROR extracting PDF: {e}")
        sys.exit(1)

    print("--- Step 2: Chunk PDF text ---")
    chunks = chunk_pdf_text(pages)
    print(f"Number of chunks: {len(chunks)}")

    print("\n--- Step 3: Build vectorstore ---")
    vectorstore = build_pdf_vectorstore(chunks)
    if vectorstore:
        print(f"Vectorstore built with {len(vectorstore['chunks'])} chunks")
    else:
        print("ERROR: Vectorstore is None")
        sys.exit(1)

    print("\n--- Step 4: Retrieve relevant chunks ---")
    results = retrieve_pdf_context(question, vectorstore, top_k=5)
    print(f"Retrieved {len(results)} chunks")
    for i, r in enumerate(results, 1):
        print(f"\n  Chunk {i}:")
        print(f"    Score: {r.get('score', 0):.4f}")
        print(f"    File: {r.get('filename', '?')}, Page: {r.get('page', '?')}")
        print(f"    Text: {r.get('text', '')[:200]}...")

    print("\n--- Step 5: Apply relevance filter ---")
    accepted, rejected = filter_by_relevance(results, question)
    print(f"Accepted: {len(accepted)}, Rejected: {rejected}")

    if not accepted:
        print("\nNo relevant evidence found after filtering.")
        sys.exit(0)

    print("\n--- Step 6: Generate answer ---")
    context = sources_to_context_block(accepted)
    citations = build_citation_string(accepted)

    answer = generate_answer(
        prompt=question,
        context=context,
        sources=citations,
        language="Bengali",
        pdf_only=True,
    )

    print(f"\n{'='*60}")
    print("FINAL ANSWER:")
    print(f"{'='*60}")
    print(answer)

    print(f"\n{'='*60}")
    print("CITATIONS:")
    print(f"{'='*60}")
    print(citations)


if __name__ == "__main__":
    main()
