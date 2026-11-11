
import streamlit as st

from config import APP_TITLE
from document_interface import (
    initialize_documents,
    display_document_upload
)
from document_processor import process_document
from chunking import create_document_chunks

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Knowledge Base")

st.write(
    "Upload company documents, extract text, "
    "and prepare them for intelligent search."
)

initialize_documents()

display_document_upload()

documents = st.session_state["uploaded_documents"]

# MILESTONE 3: DOCUMENT EXTRACTION
st.divider()
st.header("📄 Document Text Extraction")

if documents:

    if st.button("Process All Documents", type="primary"):

        for document in documents:
            try:
                extracted_pages = process_document(document)

                document["extracted_pages"] = extracted_pages
                document["extraction_status"] = (
                    "Processed" if extracted_pages else "No text found"
                )
                document.pop("extraction_error", None)

            except Exception as error:
                document["extraction_status"] = "Failed"
                document["extraction_error"] = str(error)

    for document in documents:

        with st.expander(f"📄 {document['filename']}"):

            status = document.get(
                "extraction_status",
                "Not processed"
            )

            st.write(f"**Status:** {status}")

            if document.get("extraction_error"):
                st.error(document["extraction_error"])

            for page in document.get("extracted_pages", []):

                st.markdown(f"**Page {page['page']}**")

                st.text_area(
                    f"Extracted text — {document['filename']} "
                    f"— Page {page['page']}",
                    value=page["text"],
                    height=150,
                    disabled=True,
                    key=f"text_{document['id']}_{page['page']}"
                )

else:
    st.info("Upload documents before processing them.")


# MILESTONE 4: DOCUMENT CHUNKING
st.divider()
st.header("✂️ Document Chunking")

if st.button("Generate Document Chunks", type="primary"):

    processed_documents = [
        document
        for document in documents
        if document.get("extraction_status") == "Processed"
    ]

    if not processed_documents:
        st.warning("Please process at least one document first.")

    else:
        all_chunks = create_document_chunks(processed_documents)

        st.session_state["document_chunks"] = all_chunks

        st.success(
            f"Successfully generated {len(all_chunks)} chunks."
        )

if "document_chunks" in st.session_state:

    chunks = st.session_state["document_chunks"]

    st.metric("Total Document Chunks", len(chunks))

    for index, chunk in enumerate(chunks, start=1):

        with st.expander(
            f"Chunk {index}: {chunk['filename']} "
            f"(Page {chunk['page']})"
        ):
            st.write(f"**Chunk number:** {chunk['chunk_number']}")
            st.write(f"**Source file:** {chunk['filename']}")
            st.write(f"**Page:** {chunk['page']}")
            st.write("**Extracted content:**")
            st.write(chunk["text"])
