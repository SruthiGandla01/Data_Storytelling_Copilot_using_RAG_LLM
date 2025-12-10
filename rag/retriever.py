from typing import List, Dict
import sys
from pathlib import Path

# ----------------------------------------------------------
# 0. PATCH PYTHON PATH TO PROJECT ROOT
# ----------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent      # .../Final Project/rag
PROJECT_ROOT = CURRENT_DIR.parent                  # .../Final Project

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME

_embedding_model = None
_collection = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _get_collection():
    global _collection
    if _collection is None:
        # ✅ New API: PersistentClient
        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        _collection = client.get_collection(name="insightweaver_kb")
    return _collection


def retrieve_context(query: str, top_k: int = 5) -> List[Dict]:
    model = _get_embedding_model()
    collection = _get_collection()

    query_emb = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_emb,
        n_results=top_k,
    )

    docs = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        docs.append(
            {
                "text": doc,
                "metadata": meta,
            }
        )
    return docs


if __name__ == "__main__":
    ctx = retrieve_context("Why are deliveries delayed in Southeast Asia?")
    for c in ctx:
        print("----")
        print(c["metadata"])
        print(c["text"][:250], "...")
