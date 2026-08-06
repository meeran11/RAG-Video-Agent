import os
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "transcripts"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

def get_embeddings():
    """
    Get the embeddings model.
    """
    return HuggingFaceEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu", "local_files_only": True}
    )

def build_vector_store(transcript: str, collection_name: str = COLLECTION_NAME) -> QdrantVectorStore:
    """Build a Qdrant vector store for a transcript.

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

    client = get_qdrant_client()

    collections = [
        c.name for c in client.get_collections().collections
    ]

    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

    vector_store = QdrantVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
    )

    return vector_store

def load_vector_store(collection_name: str = COLLECTION_NAME):
    embeddings = get_embeddings()

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
    )

    return vector_store

def get_retriever(vector_store, k: int = 6):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )