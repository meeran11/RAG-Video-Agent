import os
import re

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


# ----------------------------
# LLM
# ----------------------------

def get_llm():
    api_key = (os.getenv("MISTRAL_API_KEY") or "").strip()
    if not api_key:
        return None
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.2,
    )


# ----------------------------
# Text Splitter
# ----------------------------

def split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    return splitter.split_text(transcript)


def _fallback_extraction(transcript: str, mode: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", transcript) if s.strip()]
    if not sentences:
        return "None"

    if mode == "action":
        candidates = [
            s
            for s in sentences
            if re.search(r"\b(need|must|should|will|plan|next|finalize|send|review|follow up)\b", s, re.I)
        ]
        if not candidates:
            candidates = sentences[:3]
        return "\n".join(f"{i + 1}. {c}" for i, c in enumerate(candidates))

    if mode == "decision":
        candidates = [
            s
            for s in sentences
            if re.search(r"\b(decision|decided|agreed|will|plan|launch|budget|deadline)\b", s, re.I)
        ]
        if not candidates:
            candidates = sentences[:3]
        return "\n".join(f"{i + 1}. {c}" for i, c in enumerate(candidates))

    candidates = [
        s
        for s in sentences
        if "?" in s or re.search(r"\b(what|why|how|when|where|who|can|could|should)\b", s, re.I)
    ]
    if not candidates:
        candidates = sentences[:3]
    return "\n".join(f"{i + 1}. {c}" for i, c in enumerate(candidates))


# ----------------------------
# Generic LCEL Chain
# ----------------------------

def build_chain(system_prompt: str):
    llm = get_llm()
    if llm is None:
        return None

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{text}")])
    return prompt | llm | StrOutputParser()


# ----------------------------
# Process Long Transcript
# ----------------------------

def process_large_transcript(transcript: str, extraction_prompt: str, merge_prompt: str) -> str:
    chain = build_chain(extraction_prompt)
    if chain is None:
        return _fallback_extraction(transcript, "action")

    chunks = split_transcript(transcript)
    partial_results = []

    print(f"\nProcessing {len(chunks)} chunk(s)...")

    try:
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1}/{len(chunks)}")
            result = chain.invoke({"text": chunk})
            partial_results.append(result)

        combined_results = "\n\n".join(partial_results)
        merge_chain = build_chain(merge_prompt)
        if merge_chain is None:
            return "\n\n".join(partial_results)
        return merge_chain.invoke({"text": combined_results})
    except Exception:
        return _fallback_extraction(transcript, "action")


# ==========================================================
# Action Items
# ==========================================================

def extract_action_items(transcript: str) -> str:
    extraction_prompt = """
You are an expert meeting analyst.

Extract every action item mentioned.

For each action item provide:

- Task
- Owner
- Deadline (or "Not specified")

Return only the action items.
"""

    merge_prompt = """
Merge the following action items.

Remove duplicates.

Keep the most complete version of each item.

Return a clean numbered list.

{text}
"""

    return process_large_transcript(transcript, extraction_prompt, merge_prompt)


# ==========================================================
# Key Decisions
# ==========================================================

def extract_key_decisions(transcript: str) -> str:
    extraction_prompt = """
You are an expert meeting analyst.

Extract every important decision made during the meeting.

Return only the decisions.
"""

    merge_prompt = """
Merge these decisions.

Remove duplicates.

Return a concise numbered list.

{text}
"""

    return process_large_transcript(transcript, extraction_prompt, merge_prompt)


# ==========================================================
# Open Questions
# ==========================================================

def extract_questions(transcript: str) -> str:
    extraction_prompt = """
You are an expert meeting analyst.

Extract all unanswered questions,
pending discussions,
and follow-up topics.

Return only those items.
"""

    merge_prompt = """
Merge these unanswered questions.

Remove duplicates.

Return a clean numbered list.

{text}
"""

    return process_large_transcript(transcript, extraction_prompt, merge_prompt)