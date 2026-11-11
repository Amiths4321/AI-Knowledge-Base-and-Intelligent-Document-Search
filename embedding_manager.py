
import ollama

from config import OLLAMA_HOST, EMBEDDING_MODEL


def generate_embedding(text):
    """Generate an embedding for a single text chunk."""

    client = ollama.Client(host=OLLAMA_HOST)

    response = client.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )

    return response["embedding"]


def generate_document_embeddings(chunks):
    """Generate embeddings for all document chunks."""

    if not chunks:
        return [], []

    client = ollama.Client(host=OLLAMA_HOST)

    embeddings = []
    successful_chunks = []

    for index, chunk in enumerate(chunks, start=1):

        try:
            response = client.embeddings(
                model=EMBEDDING_MODEL,
                prompt=chunk["text"]
            )

            embeddings.append(response["embedding"])
            successful_chunks.append(chunk)

        except Exception as error:
            print(
                f"Embedding failed for chunk {index}: {error}"
            )

    return embeddings, successful_chunks


def generate_query_embedding(text):
    """Generate an embedding for a search question."""

    client = ollama.Client(host=OLLAMA_HOST)

    response = client.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )

    return response["embedding"]
