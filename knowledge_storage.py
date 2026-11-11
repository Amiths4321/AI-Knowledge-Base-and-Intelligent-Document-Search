
import json
import os
import faiss


KNOWLEDGE_FOLDER = "knowledge_base"

INDEX_PATH = os.path.join(
    KNOWLEDGE_FOLDER,
    "company.index"
)

CHUNKS_PATH = os.path.join(
    KNOWLEDGE_FOLDER,
    "company_chunks.json"
)


def save_knowledge_base(index, chunks):
    """Save FAISS index and matching document chunks."""

    os.makedirs(KNOWLEDGE_FOLDER, exist_ok=True)

    if index.ntotal != len(chunks):
        raise ValueError(
            "FAISS vector count does not match chunk count."
        )

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)


def load_knowledge_base():
    """Load the saved FAISS index and document chunks."""

    if not os.path.exists(INDEX_PATH):
        return None, []

    if not os.path.exists(CHUNKS_PATH):
        return None, []

    index = faiss.read_index(INDEX_PATH)

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    if index.ntotal != len(chunks):
        raise ValueError(
            "Saved FAISS index and chunks do not match."
        )

    return index, chunks
