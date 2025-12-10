"""
Build the Chroma vector store from markdown knowledge base files.

- Reads all .md files under kb/
- Embeds them with sentence-transformers
- Stores them in a Chroma DB collection called 'insightweaver_kb'
"""

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

from config import KB_BASE_PATH, CHROMA_DB_DIR, EMBEDDING_MODEL_NAME


def load_kb_texts():
    """Load all markdown files from kb/ into memory."""
    texts = []
    metadatas = []
    ids = []

    kb_files = list(KB_BASE_PATH.rglob("*.md"))
    for i, fpath in enumerate(kb_files):
        text = fpath.read_text(encoding="utf-8")
        texts.append(text)
        metadatas.append(
            {
                "relative_path": str(fpath.relative_to(KB_BASE_PATH)),
                "category": fpath.parts[-2],  # schema_docs, metric_definitions, business_playbook
            }
        )
        ids.append(str(i))

    return texts, metadatas, ids


def build_chroma_store():
    """Create/update the Chroma DB collection from KB markdown files."""
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

    # ✅ New API: PersistentClient instead of Client(Settings(...))
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    # You can pass metadata if you want; not required
    collection = client.get_or_create_collection(
        name="insightweaver_kb",
        metadata={"description": "KB for InsightWeaver supply chain project"},
    )

    texts, metadatas, ids = load_kb_texts()
    print(f"Loaded {len(texts)} KB documents from {KB_BASE_PATH}")

    if not texts:
        print("WARNING: No .md files found in kb/. Did you create the KB markdown files?")
        return

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embeddings = model.encode(texts).tolist()

    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings,
    )

    print(f"Chroma store built and persisted at {CHROMA_DB_DIR}")


if __name__ == "__main__":
    print("Project root detected as:", PROJECT_ROOT)
    build_chroma_store()
