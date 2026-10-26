from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def build_rag_chain(retriever, llm, format_function):
    """"""""

    RAG_PROMPT_TEMPLATE = \
        """
            Você é um assistente de IA especializado em análise financeira.
            Sua tarefa é responder perguntas sobre demonstrativos financeiros usando APENAS o contexto fornecido.
            Seja direto, preciso e baseie-se exclusivamente nos dados dos trechos.
            Se a informação não estiver no contexto, diga "A informação não foi encontrada no documento."

            Contexto:
            {context}

            Pergunta:
            {question}

            Resposta (em Português):
        """

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    rag_chain = (
        {"context": retriever | format_function, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain