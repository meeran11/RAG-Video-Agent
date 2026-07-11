import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

# ----------------------------
# LLM
# ----------------------------

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
    )


# ----------------------------
# Text Splitter
# ----------------------------

def split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
    )

    return splitter.split_text(transcript)


# ----------------------------
# Generic LCEL Chain
# ----------------------------

def build_chain(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{text}")
        ]
    )

    return (
        prompt
        | get_llm()
        | StrOutputParser()
    )


# ----------------------------
# Process Long Transcript
# ----------------------------

def process_large_transcript(
    transcript: str,
    extraction_prompt: str,
    merge_prompt: str,
) -> str:

    chunks = split_transcript(transcript)

    extraction_chain = build_chain(extraction_prompt)

    partial_results = []

    print(f"\nProcessing {len(chunks)} chunk(s)...")

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}/{len(chunks)}")

        result = extraction_chain.invoke(
            {
                "text": chunk
            }
        )

        partial_results.append(result)

    combined_results = "\n\n".join(partial_results)

    merge_chain = build_chain(merge_prompt)

    final_result = merge_chain.invoke(
        {
            "text": combined_results
        }
    )

    return final_result


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

    return process_large_transcript(
        transcript,
        extraction_prompt,
        merge_prompt,
    )


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

    return process_large_transcript(
        transcript,
        extraction_prompt,
        merge_prompt,
    )


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

    return process_large_transcript(
        transcript,
        extraction_prompt,
        merge_prompt,
    )