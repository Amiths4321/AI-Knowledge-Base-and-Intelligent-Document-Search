
import faiss
import numpy as np


def build_vector_index(embeddings):
    """Build a FAISS index using normalized embeddings."""

    if not embeddings:
        raise ValueError("No embeddings provided.")

    embedding_array = np.asarray(
        embeddings,
        dtype="float32"
    )

    if embedding_array.ndim != 2:
        raise ValueError("Embeddings must be a two-dimensional array.")

    if not np.isfinite(embedding_array).all():
        raise ValueError("Embeddings contain invalid numeric values.")

    # Normalize vectors for cosine similarity.
    faiss.normalize_L2(embedding_array)

    # Inner product of normalized vectors = cosine similarity.
    dimension = embedding_array.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_array)

    return index


def search_vector_index(index, query_embedding, top_k=5):
    """Search the FAISS index using a query embedding."""

    if index.ntotal == 0:
        return [], []

    query_array = np.asarray(
        [query_embedding],
        dtype="float32"
    )

    if query_array.shape[1] != index.d:
        raise ValueError(
            "Query embedding dimension does not match the index."
        )

    if not np.isfinite(query_array).all():
        raise ValueError("Query embedding contains invalid values.")

    faiss.normalize_L2(query_array)

    scores, indices = index.search(
        query_array,
        min(top_k, index.ntotal)
    )

    return scores[0].tolist(), indices[0].tolist()
