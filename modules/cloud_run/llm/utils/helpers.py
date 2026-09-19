import os

def setup_environment() -> None:
    """"""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

def check_groq_api_key() -> None:
    """"""
    if "GROQ_API_KEY" not in os.environ:
        import streamlit as st
        st.error("A GROQ_API_KEY não foi encontrada.")
        st.info("Por favor, crie um arquivo .env e adicione sua chave API do Groq.")
        st.stop()

def format_docs(docs) -> str:
    """"""
    return "\n\n---\n\n".join([d.page_content for d in docs])