import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

@st.cache_resource
def get_embedding_model():
    """"""
    st.write(f" Loading embedding model ({EMBEDDING_MODEL})...")

    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name      = EMBEDDING_MODEL,
        model_kwargs    = model_kwargs,
        encode_kwargs   = encode_kwargs
    )