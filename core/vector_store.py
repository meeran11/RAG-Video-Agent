import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHROMA_DIR = "vector-db"
COLLECTION_NAME = "transcripts"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings():
    """
    Get the embeddings model.
    """
    return HuggingFaceEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu", "local_files_only": True}
    )

def build_vector_store(transcript: str, collection_name: str = COLLECTION_NAME) -> Chroma:
    """Build a Chroma vector store for a transcript.

    collection_name lets callers (e.g. the API, which handles multiple videos
    at once) keep each video's embeddings in its own collection instead of
    mixing them together in the default "transcripts" collection used by the
    CLI (main.py).
    """
    print(f"Building Vector Store (collection: {collection_name})")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 150
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk,metadata = {'chunk_index':i})
        for i,chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def load_vector_store(collection_name: str = COLLECTION_NAME) -> Chroma:
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function= embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def get_retriever(vector_store : Chroma, k :int = 6):
    return vector_store.as_retriever(
        search_type = 'similarity',
        search_kwargs = {"k":k}
    )