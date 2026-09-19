import os
import tempfile
import polars as pl
import streamlit as st
from langchain_core.documents import Document
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter



import polars as pl

from langchain_core.documents import Document


def dataframe_to_documents(
    df: pl.DataFrame,
    source: str
) -> list[Document]:
    """
    Convert a Polars DataFrame into LangChain Documents.
    """

    documents = []

    try:
        for row_id, row in enumerate(df.iter_rows(named=True)):

            content = "\n".join(
                f"{column}: {value}"
                for column, value in row.items()
                if value is not None
            )

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": source,
                        "row_id": row_id,
                        "origin": "bigquery"
                    }
                )
            )

        return documents
    except Exception as e:
        st.error(f"Error converting DataFrame to documents: {e}")
        return []

# def process_pdf(uploaded_file):
#     """Processa o arquivo PDF e retorna os splits dos documentos."""
#     if uploaded_file is None:
#         return None

#     try:
#         # Cria arquivo temporário
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#             tmp_file.write(uploaded_file.getvalue())
#             tmp_file_path = tmp_file.name

#         # Carrega e processa o PDF
#         loader = PyPDFLoader(tmp_file_path)
#         docs = loader.load()

#         # Divide em chunks
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=800,
#             chunk_overlap=200
#         )
#         splits = text_splitter.split_documents(docs)

#         # Limpa arquivo temporário
#         os.remove(tmp_file_path)

#         return splits

#     except Exception as e:
#         st.error(f"Erro ao processar o PDF: {e}")
#         return None