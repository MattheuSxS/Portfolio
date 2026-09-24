import logging
import streamlit as st
from utils.vectorstore.bq_processor import dataframe_to_documents
from dotenv import load_dotenv
from sympy import im

# Importações dos módulos
from utils.helpers import (
    setup_environment,
    check_groq_api_key,
    format_docs
)
from utils.llm.groq_client import get_llm
from utils.llm.chain_builder import build_rag_chain
from utils.embeddings.embedding_model import get_embedding_model
from utils.vectorstore.chroma_manager import (
    create_vector_store,
    load_existing_vector_store
)
from utils.bigquery import BigQuery

# Configurações iniciais
setup_environment()
load_dotenv()
check_groq_api_key()

@st.cache_data(ttl=1800)
def load_bigquery_data(_bq_client):

    return {
        "feedback"  : _bq_client.read_bq("sql_feedback"),
        "customers" : _bq_client.read_bq("sql_customer"),
        "sales"     : _bq_client.read_bq("sql_region_sales"),
        # "products"  : _bq_client.read_bq("sql_products_sales"),
        "forecast"  : _bq_client.read_bq("sql_sales_forecast"),
    }

def build_bigquery_documents(dataframes: dict) -> list[dict]:

    documents = []

    for source, df in dataframes.items():

        documents.extend(
            dataframe_to_documents(
                df=df,
                source=source
            )
        )

    return documents

def main():
    """"""

    _bq_client = BigQuery(project="gcp-mts-pf")
    df_bq = load_bigquery_data(_bq_client)


    documents = build_bigquery_documents(df_bq)

    # Configuração da página
    st.set_page_config(
        page_title  = "LogiStream AI Assistant",
        page_icon   = "🚛",
        layout      = "wide"
    )

    # Título da aplicação
    st.title("🤖 RAG App for Semantic Search on BigQuery Data")
    st.markdown("Harness the power of RAG with Groq, ChromaDB (Persistent), and HuggingFace embeddings.")

    # Inicializa modelos
    llm = get_llm()
    embeddings = get_embedding_model()

    # Sidebar
    with st.sidebar:
        st.header("Carregar Documento")

        uploaded_file = st.file_uploader(
            label = "Carregue seu demonstrativo financeiro (.pdf)",
            type = "pdf",
            accept_multiple_files = False
        )

        st.warning("Note: Processing the data loaded from BigQuery (creating embeddings) may take a few minutes the first time.")

        with st.expander("🆘 Assistance / Contact Us", expanded=False):
            st.write("If you have any questions, please send a message to mattheusxs@gmail.com")

        st.info("Notice: AI may generate inaccurate, incomplete, or incorrect responses. Always verify critical information before fully relying on the result.")

    # Inicialização do retriever no session_state
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None

    # Lógica de carregamento/processamento do documento
    if documents:
        st.session_state.retriever = create_vector_store(documents, embeddings)
    elif not documents and st.session_state.retriever is None:
        st.session_state.retriever = load_existing_vector_store(embeddings)

    # Question section
    st.header("Ask Your Question")

    if st.session_state.retriever:
        # Construir cadeia RAG
        rag_chain = build_rag_chain(
            st.session_state.retriever,
            llm,
            format_docs
        )

        # Campo de pergunta
        question = st.text_input(
            "Ask your question. Ex: What was the revenue recognition criteria? or What is the operational cash flow?",
            disabled=False
        )

        if question:
            with st.spinner("Performing semantic search and generating response..."):
                try:
                    answer = rag_chain.invoke(question)

                    st.success("Generated Answer:")
                    st.write(answer)

                    # Mostrar chunks usados
                    with st.expander("View Context Chunks Used"):
                        retrieved_docs = st.session_state.retriever.invoke(question)
                        st.json([doc.to_json() for doc in retrieved_docs])

                except Exception as e:
                    st.error(f"An error occurred while invoking the RAG chain: {e}")
    else:
        st.info("Please wait for the document to be loaded.")
        st.text_input("Ask your question...", disabled=True)

if __name__ == "__main__":
    main()