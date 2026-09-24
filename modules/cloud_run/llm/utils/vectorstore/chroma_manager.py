import os
import streamlit as st
from langchain_chroma import Chroma


CHROMA_PERSIST_DIR = "chroma_db_persist"
CHROMA_COLLECTION_NAME = "demonstrativos_financeiros"

@st.cache_resource(show_spinner="Processing BigQuery loaded data and creating Vector Store...")
def create_vector_store(documents, embedding_model):
    """Creates a vector store from the given documents and embedding model.

    Args:
        documents (list): A list of documents to be added to the vector store.
        embedding_model (object): The embedding model to use for creating the vector store.

    Returns:
        retriever (object): A retriever object for querying the vector store,
        or None if no documents are provided.
    """

    if documents:
        vectorstore = \
            Chroma.from_documents(
                documents           = documents,
                embedding           = embedding_model,
                persist_directory   = CHROMA_PERSIST_DIR,
                collection_name     = CHROMA_COLLECTION_NAME
            )

        return vectorstore.as_retriever(search_kwargs={"k": 3})

    return None

@st.cache_resource(show_spinner="Loading existing Vector Store from disk...")
def load_existing_vector_store(embedding_model):
    """Loads an existing vector store from the persistent directory.

    Args:
        embedding_model (object): The embedding model to use for loading the vector store.

    Returns:
        retriever (object): A retriever object for querying the vector store,
        or None if the persistent directory does not exist.
    """

    if os.path.exists(CHROMA_PERSIST_DIR):
        st.write("Loading persisted Vector Store from disk...")

        vectorstore = Chroma(
            persist_directory   = CHROMA_PERSIST_DIR,
            embedding_function  = embedding_model,
            collection_name     = CHROMA_COLLECTION_NAME
        )

        st.sidebar.success("Local vector store loaded!")
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    return None