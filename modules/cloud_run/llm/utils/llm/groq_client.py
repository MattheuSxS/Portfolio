import streamlit as st
from langchain_groq import ChatGroq

@st.cache_resource
def get_llm():
    """Inicializa e cacheia o modelo de linguagem (LLM) do Groq."""
    st.write("Inicializando LLM do Groq...")
    return ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0
    )