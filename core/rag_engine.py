import os
import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from core.vector_store import build_vector_store, get_retriever, load_vector_store


class SimpleRAGChain:
    def __init__(self, transcript: str, summary: str | None = None):
        self.transcript = transcript
        self.summary = summary
        self.chunks = [c.strip() for c in re.split(r"(?<=[.!?])\s+|\n+", transcript) if c.strip()]

    def _retrieve(self, question: str) -> list[str]:
        words = re.findall(r"[a-zA-Z0-9]+", question.lower())
        if not words:
            return self.chunks[:3]

        scored = []
        for chunk in self.chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for word in words if word in chunk_lower)
            if score:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        if scored:
            return [chunk for _, chunk in scored[:3]]
        return self.chunks[:3]

    def invoke(self, question: str) -> str:
        context = "\n\n".join(self._retrieve(question))
        if self.summary:
            return (
                f"Based on the available transcript, here's a concise answer:\n"
                f"{context[:800]}"
            )
        return f"Based on the available transcript:\n{context[:800]}"

    def __call__(self, question: str) -> str:
        return self.invoke(question)


def get_llm():
    api_key = (os.getenv("MISTRAL_API_KEY") or "").strip()
    if not api_key:
        return None
    return ChatMistralAI(model="mistral-small-latest", mistral_api_key=api_key, temperature=0.3)


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def _system_prompt(summary: str | None = None) -> str:
    safe_summary = summary.replace("{", "{{").replace("}", "}}") if summary else None
    summary_block = (
        f"""
Overview summary of the entire video/meeting (use this for broad or general
questions like "what is this video about", "give me an overview", or
"summarize this"):
{safe_summary}
"""
        if safe_summary
        else ""
    )

    return f"""You are an expert video/meeting assistant helping someone understand a video
they've uploaded.

You have up to two sources of information:
{summary_block}
Specific excerpts retrieved from the transcript for this question (use these
for specific facts, quotes, names, numbers, or details):
{{context}}

Guidelines:
- For broad/general questions, answer using the overview summary above.
- For specific questions, ground your answer in the retrieved excerpts, and use the overview for extra context if helpful.
- If neither source actually covers what's being asked, say so honestly rather than guessing.
- Be concise and clear. If quoting someone, mention it explicitly.
"""


def build_rag_chain(transcript: str, collection_name: str | None = None, summary: str | None = None):
    has_mistral = bool((os.getenv("MISTRAL_API_KEY") or "").strip())
    has_qdrant = bool((os.getenv("QDRANT_URL") or "").strip()) and bool((os.getenv("QDRANT_API_KEY") or "").strip())
    if not has_mistral or not has_qdrant:
        return SimpleRAGChain(transcript, summary=summary)

    try:
        vector_store = (
            build_vector_store(transcript, collection_name=collection_name)
            if collection_name
            else build_vector_store(transcript)
        )
        retriever = get_retriever(vector_store, k=6)
        llm = get_llm()
        if llm is None:
            return SimpleRAGChain(transcript, summary=summary)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", _system_prompt(summary)),
                ("human", "{question}"),
            ]
        )

        return (
            {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
    except Exception:
        return SimpleRAGChain(transcript, summary=summary)


def load_rag_chain(summary: str | None = None):
    has_mistral = bool((os.getenv("MISTRAL_API_KEY") or "").strip())
    has_qdrant = bool((os.getenv("QDRANT_URL") or "").strip()) and bool((os.getenv("QDRANT_API_KEY") or "").strip())
    if not has_mistral or not has_qdrant:
        return SimpleRAGChain("", summary=summary)

    try:
        vector_store = load_vector_store()
        retriever = get_retriever(vector_store, k=6)
        llm = get_llm()
        if llm is None:
            return SimpleRAGChain("", summary=summary)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", _system_prompt(summary)),
                ("human", "{question}"),
            ]
        )
        return (
            {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
    except Exception:
        return SimpleRAGChain("", summary=summary)


def ask_question(rag_chain, question: str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question) if hasattr(rag_chain, "invoke") else rag_chain(question)
    print(f"answer :{answer}")
    return answer