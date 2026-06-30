import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from config import DEFAULT_LLM_MODEL, DEFAULT_EMBEDDING_MODEL

load_dotenv()

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Add it to .env or export it."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def generate_answer(
    prompt: str,
    context: str,
    sources: str,
    language: str = "Bengali",
    model: str = DEFAULT_LLM_MODEL,
    pdf_only: bool = False,
) -> str:
    source_instruction = ""
    if pdf_only:
        source_instruction = """
CRITICAL PDF-ONLY RULES:
- All evidence comes from the uploaded PDF document.
- Cite ONLY using PDF citations like [PDF: filename.pdf, page N].
- Do NOT cite any web sources — there are none in the evidence.
- Do NOT reference external websites, news articles, or online sources.
- If the evidence does not answer the question, say: "আপলোড করা PDF থেকে এই প্রশ্নের সরাসরি উত্তর পাওয়া যায়নি।"
"""

    system_msg = f"""You are BanglaAgent, a factual research assistant for Bengali-speaking users.

STRICT RULES — VIOLATIONS ARE UNACCEPTABLE:
1. Answer ONLY in {language}.
2. Base your answer EXCLUSIVELY on the provided evidence below. Do NOT use your own knowledge for any factual claim.
3. Cite sources inline using the exact citation tags from the evidence (e.g., [PDF: file.pdf, page N] or [Source: Title, URL]).
4. If NO evidence supports a claim, do NOT make that claim. Say explicitly that evidence was not found.
5. NEVER invent, fabricate, or guess citations. Every citation must appear in the evidence list.
6. NEVER use a source or fact not present in the evidence list.
7. If the evidence is about a DIFFERENT topic than the question, respond: "প্রদত্ত সূত্রে এই প্রশ্নের প্রাসঙ্গিক তথ্য পাওয়া যায়নি।"
8. If evidence is insufficient, say: "আমি নির্ভরযোগ্য সূত্রে এই তথ্যটি পাইনি। অনুগ্রহ করে আরেকটি সূত্র বা PDF দিন।"
{source_instruction}
ANSWER STRUCTURE (use these exact Bengali headings):

## সংক্ষিপ্ত উত্তর
(2-3 sentence summary with citations)

## বিস্তারিত ব্যাখ্যা
(Detailed explanation with inline citations for every factual paragraph)

## মূল পয়েন্ট
(Bulleted key points)

## সূত্র
(Numbered list of all sources actually used)

## সীমাবদ্ধতা
(Any limitations of the evidence)

Use simple, clear language suitable for students and journalists."""

    user_msg = f"""Question: {prompt}

--- Retrieved Evidence ---
{context}

--- Available Sources ---
{sources}

Answer the question based EXCLUSIVELY on the evidence above. Do not add any information not present in the evidence."""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    return response.choices[0].message.content or ""


def generate_summary(
    context: str,
    question: str,
    language: str = "Bengali",
    model: str = DEFAULT_LLM_MODEL,
) -> str:
    system_msg = f"""You are BanglaAgent. Summarize the provided evidence to answer the question.
Answer in {language}. Be concise but thorough. Cite sources using the citation tags from the evidence.
Do NOT add information not present in the evidence. If evidence is insufficient, say so."""

    user_msg = f"""Question: {question}

Evidence:
{context}

Provide a clear summary based only on this evidence."""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


def generate_podcast_script(
    context: str,
    question: str,
    language: str = "Bengali",
    model: str = DEFAULT_LLM_MODEL,
) -> str:
    system_msg = f"""You are BanglaAgent. Generate a Bengali podcast script.

RULES:
- Write in {language}, natural conversational tone for a Bangladeshi podcast host.
- Use the provided evidence only. Do NOT invent facts.
- Structure:
  ## বাংলা পডকাস্ট স্ক্রিপ্ট
  **শিরোনাম:** ...
  **হুক:** ... (attention grabbing opening line)
  **উপস্থাপকের ভূমিকা:** ...
  **পর্ব ১:** ...
  **পর্ব ২:** ...
  **পর্ব ৩:** ...
  **সূত্র উল্লেখ:** ...
  **সমাপনী সারসংক্ষেপ:** ...
  **প্রস্তাবিত সময়কাল:** ...
- Start with: "স্বাগতম আজকের আলোচনায়। আজ আমরা সহজ ভাষায় বুঝব..."
- Make it sound natural, engaging, informative.
- Cite sources where facts are mentioned.
"""

    user_msg = f"""Topic/Question: {question}

Evidence:
{context}

Generate the podcast script."""

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.5,
        max_tokens=3000,
    )
    return response.choices[0].message.content or ""


def create_embeddings(
    texts: list[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    if not texts:
        return []

    client = get_client()
    batch_size = 100
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=model, input=batch)
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings
