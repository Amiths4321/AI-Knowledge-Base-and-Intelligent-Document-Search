
import streamlit as st

from config import APP_TITLE, TOP_K

from document_interface import (
    initialize_documents,
    display_document_upload
)

from document_processor import process_document
from chunking import create_document_chunks
from embedding_manager import generate_document_embeddings
from vector_store import build_vector_index
from search_manager import search_documents
from rag_engine import generate_rag_answer

from knowledge_storage import (
    save_knowledge_base,
    load_knowledge_base
)

from dashboard import (
    show_dashboard,
    generate_excel_report
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Knowledge Base")
st.write(
    "Upload company documents, build a searchable knowledge base, "
    "and ask questions using AI."
)


# --------------------------------------------------
# INITIALIZE SESSION STATE
# --------------------------------------------------

initialize_documents()

if "question_history" not in st.session_state:
    st.session_state["question_history"] = []

if "knowledge_loaded" not in st.session_state:

    try:
        saved_index, saved_chunks = load_knowledge_base()

        if saved_index is not None:
            st.session_state["vector_index"] = saved_index
            st.session_state["embedding_chunks"] = saved_chunks
            st.session_state["document_chunks"] = saved_chunks

        st.session_state["knowledge_loaded"] = True

    except Exception as error:
        st.session_state["knowledge_loaded"] = True
        st.error(f"Could not load saved knowledge base: {error}")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📚 Navigation")

section = st.sidebar.radio(
    "Choose a section",
    [
        "Document Management",
        "Ask Questions",
        "Dashboard and Reports"
    ]
)


# --------------------------------------------------
# SECTION 1: DOCUMENT MANAGEMENT
# --------------------------------------------------

if section == "Document Management":

    st.header("📤 Document Management")

    display_document_upload()

    documents = st.session_state["uploaded_documents"]

    st.divider()
    st.subheader("Step 1 — Extract Document Text")

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

        st.success("Document processing finished.")
        st.rerun()

    for document in documents:

        with st.expander(document["filename"]):

            st.write(
                "Status:",
                document.get("extraction_status", "Not processed")
            )

            if document.get("extraction_error"):
                st.error(document["extraction_error"])

            for page in document.get("extracted_pages", []):

                st.markdown(f"**Page {page['page']}**")
                st.text(page["text"])


    st.divider()
    st.subheader("Step 2 — Generate Document Chunks")

    if st.button("Generate Document Chunks", type="primary"):

        processed_documents = [
            document
            for document in documents
            if document.get("extraction_status") == "Processed"
        ]

        if not processed_documents:
            st.warning("Process at least one document first.")

        else:

            chunks = create_document_chunks(processed_documents)

            st.session_state["document_chunks"] = chunks

            # Invalidate older embeddings and indexes.
            st.session_state.pop("document_embeddings", None)
            st.session_state.pop("embedding_chunks", None)
            st.session_state.pop("vector_index", None)

            st.success(f"Generated {len(chunks)} chunks.")


    chunks = st.session_state.get("document_chunks", [])

    if chunks:
        st.metric("Generated Chunks", len(chunks))


    st.divider()
    st.subheader("Step 3 — Generate Embeddings")

    if st.button("Generate Embeddings", type="primary"):

        if not chunks:
            st.warning("Generate document chunks first.")

        else:

            try:
                with st.spinner("Generating embeddings with Ollama..."):

                    embeddings, successful_chunks = (
                        generate_document_embeddings(chunks)
                    )

                st.session_state["document_embeddings"] = embeddings
                st.session_state["embedding_chunks"] = successful_chunks

                st.session_state.pop("vector_index", None)

                st.success(
                    f"Generated {len(embeddings)} embeddings."
                )

                if len(embeddings) < len(chunks):
                    st.warning(
                        "Some chunks could not be embedded. "
                        "Only successfully embedded chunks will be indexed."
                    )

            except Exception as error:
                st.error(f"Embedding generation failed: {error}")


    embeddings = st.session_state.get("document_embeddings", [])

    if embeddings:
        st.metric("Embedding Dimensions", len(embeddings[0]))


    st.divider()
    st.subheader("Step 4 — Build and Save FAISS Database")

    if st.button("Build and Save Knowledge Base", type="primary"):

        if not embeddings:
            st.warning("Generate embeddings first.")

        else:

            try:
                with st.spinner("Building and saving knowledge base..."):

                    index = build_vector_index(embeddings)

                    matching_chunks = st.session_state[
                        "embedding_chunks"
                    ]

                    save_knowledge_base(index, matching_chunks)

                st.session_state["vector_index"] = index
                st.session_state["document_chunks"] = matching_chunks

                st.success(
                    f"Knowledge base saved with {index.ntotal} vectors."
                )

            except Exception as error:
                st.error(f"Could not build or save knowledge base: {error}")


    if "vector_index" in st.session_state:

        st.info(
            f"Active FAISS index: "
            f"{st.session_state['vector_index'].ntotal} vectors"
        )


# --------------------------------------------------
# SECTION 2: ASK QUESTIONS
# --------------------------------------------------

elif section == "Ask Questions":

    st.header("🤖 Ask Your Documents")

    if (
        "vector_index" not in st.session_state
        or "embedding_chunks" not in st.session_state
    ):

        st.warning(
            "No active knowledge base found. "
            "Build one in Document Management or load a saved one."
        )

    else:

        question = st.text_input(
            "Enter your question",
            placeholder="What is the company's leave policy?"
        )

        if st.button("Ask AI", type="primary"):

            if not question.strip():
                st.warning("Enter a question first.")

            else:

                try:
                    with st.spinner(
                        "Searching documents and generating an answer..."
                    ):

                        results = search_documents(
                            query=question,
                            vector_index=st.session_state["vector_index"],
                            chunks=st.session_state["embedding_chunks"],
                            top_k=TOP_K
                        )

                        answer = generate_rag_answer(
                            question,
                            results
                        )

                    st.session_state["current_answer"] = answer
                    st.session_state["current_sources"] = results

                    st.session_state["question_history"].append({
                        "Question": question,
                        "Answer": answer
                    })

                except Exception as error:
                    st.error(f"Question answering failed: {error}")


        if st.session_state.get("current_answer"):

            st.divider()
            st.subheader("💡 AI Answer")

            st.write(st.session_state["current_answer"])

            st.subheader("📚 Supporting Sources")

            for index, source in enumerate(
                st.session_state.get("current_sources", []),
                start=1
            ):

                with st.expander(
                    f"[S{index}] {source['filename']} "
                    f"— Page {source['page']}"
                ):

                    st.write(source["text"])

                    st.caption(
                        f"Similarity score: "
                        f"{source.get('similarity_score', 0):.4f}"
                    )


# --------------------------------------------------
# SECTION 3: DASHBOARD AND REPORTS
# --------------------------------------------------

elif section == "Dashboard and Reports":

    documents = st.session_state["uploaded_documents"]

    chunks = st.session_state.get(
        "document_chunks",
        st.session_state.get("embedding_chunks", [])
    )

    vector_index = st.session_state.get("vector_index")

    question_history = st.session_state["question_history"]

    show_dashboard(
        documents,
        chunks,
        vector_index,
        question_history
    )

    st.divider()
    st.subheader("📥 Export Knowledge Base Report")

    excel_report = generate_excel_report(
        documents,
        chunks,
        question_history
    )

    st.download_button(
        label="Download Excel Report",
        data=excel_report,
        file_name="knowledge_base_report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )
