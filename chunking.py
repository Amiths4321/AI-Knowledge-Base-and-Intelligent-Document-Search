
from config import CHUNK_SIZE, CHUNK_OVERLAP


def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Divide text into overlapping word-based chunks."""

    words = text.split()

    if not words:
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be zero or greater and smaller than chunk size."
        )

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_text = " ".join(words[start:end])
        chunks.append(chunk_text)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def create_document_chunks(documents):
    """Create chunks from all extracted document pages."""

    all_chunks = []

    for document in documents:

        extracted_pages = document.get("extracted_pages", [])

        for page in extracted_pages:

            page_chunks = create_chunks(page["text"])

            for chunk_number, chunk_text in enumerate(
                page_chunks,
                start=1
            ):
                all_chunks.append({
                    "filename": document["filename"],
                    "document_id": document["id"],
                    "page": page["page"],
                    "chunk_number": chunk_number,
                    "text": chunk_text
                })

    return all_chunks
