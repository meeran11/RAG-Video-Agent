import os
import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_llm():
    api_key = (os.getenv("MISTRAL_API_KEY") or "").strip()
    if not api_key:
        return None

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.2,
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    return splitter.split_text(transcript)


def _fallback_summary(transcript: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", transcript) if s.strip()]
    if not sentences:
        return "Transcript is empty."

    selected = sentences[:4]
    bullets = "\n".join(f"- {sentence}" for sentence in selected)
    return f"Summary (heuristic fallback):\n{bullets}"


def summarize(transcript: str) -> str:
    llm = get_llm()
    if llm is None:
        return _fallback_summary(transcript)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize this portion of a transcription concisely."),
            ("human", "{text}"),
        ]
    )

    parser = StrOutputParser()
    chain = prompt | llm | parser

    try:
        chunks = split_transcript(transcript)
        chunk_summaries = [chain.invoke({"text": chunk}) for chunk in chunks]
        summary = "\n\n".join(chunk_summaries)

        combined_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert meeting summarizer. Combine these partial summaries "
                    "into one final professional meeting summary in bullet points.",
                ),
                ("human", "{text}"),
            ]
        )

        combined_chain = combined_prompt | llm | StrOutputParser()
        return combined_chain.invoke({"text": summary})
    except Exception:
        return _fallback_summary(transcript)


def generate_title(transcript: str) -> str:
    llm = get_llm()
    if llm is None:
        cleaned = re.sub(r"[^A-Za-z0-9\s'-]", "", transcript).strip()
        words = cleaned.split()[:8]
        return " ".join(words) if words else "Video Transcript"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    try:
        return chain.invoke(transcript[:200])
    except Exception:
        cleaned = re.sub(r"[^A-Za-z0-9\s'-]", "", transcript).strip()
        words = cleaned.split()[:8]
        return " ".join(words) if words else "Video Transcript"