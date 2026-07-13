import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.vector_store import build_vector_store, load_vector_store, get_retriever

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def _system_prompt(summary: str | None = None) -> str:
    """Builds the system prompt. When a video summary is available it's baked
    in directly (it's static for a given video, so it doesn't need to be a
    per-invocation chain variable) so the model always has a grasp of the
    whole video, not just whatever chunks similarity search happened to
    retrieve for this one question."""

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

    vector_store = (
        build_vector_store(transcript, collection_name=collection_name)
        if collection_name
        else build_vector_store(transcript)
    )

    retriever = get_retriever(vector_store, k = 6)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _system_prompt(summary)),
            ("human", "{question}"),
        ]
    )

    #full LCEL Rag pipeline 

    rag_chain = (

        {"context" : retriever | RunnableLambda(format_docs),
         "question": RunnablePassthrough()
         }
         |prompt|llm|StrOutputParser()
    )

    return rag_chain


def load_rag_chain(summary: str | None = None):
    vector_store = load_vector_store()
    retriver = get_retriever(vector_store,k=6)

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", _system_prompt(summary)),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriver| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer