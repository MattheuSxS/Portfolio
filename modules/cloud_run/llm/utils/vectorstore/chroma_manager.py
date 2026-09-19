import os
import streamlit as st
from langchain_chroma import Chroma
from .bq_processor import process_pdf

CHROMA_PERSIST_DIR = "chroma_db_persist"
CHROMA_COLLECTION_NAME = "demonstrativos_financeiros"

@st.cache_resource(show_spinner="Processing BigQuery loaded data and creating Vector Store...")
def create_vector_store(uploaded_file, embedding_model):
    """"""

    splits = process_pdf(uploaded_file)

    if splits:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_model,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=CHROMA_COLLECTION_NAME
        )

        st.success(f"PDF processed! {len(splits)} chunks created and saved in ChromaDB.")
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    return None

def load_existing_vector_store(embedding_model):
    """Loads an existing vector store from the persistent directory."""

    if os.path.exists(CHROMA_PERSIST_DIR):
        st.write("Loading persisted Vector Store from disk...")

        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embedding_model,
            collection_name=CHROMA_COLLECTION_NAME
        )

        st.sidebar.success("Local vector store loaded!")
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    return None