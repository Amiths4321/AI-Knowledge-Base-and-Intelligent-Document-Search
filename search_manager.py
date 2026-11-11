
from embedding_manager import generate_query_embedding
from vector_store import search_vector_index


def search_documents(query, vector_index, chunks, top_k=5):
    """Find the most relevant document chunks for a question."""

    if not query.strip():
        return []

    if vector_index is None:
        raise ValueError("FAISS vector index is not available.")

    if not chunks:
        return []

    query_embedding = generate_query_embedding(query)

    scores, indices = search_vector_index(
        vector_index,
        query_embedding,
        top_k=top_k
    )

    results = []

    for score, index in zip(scores, indices):

        if index < 0 or index >= len(chunks):
            continue

        result = chunks[index].copy()
        result["similarity_score"] = float(score)

        results.append(result)

    return results
