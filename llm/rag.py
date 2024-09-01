import logging
from config import settings
from database.vectorstore import retriever

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

llm = ChatOllama(model=settings.LLM_MODEL, temperature=0)

prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 
    Answer the question in email format and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} 
    Context: {context} 
    Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "document"],
)


def generate_response(question, llm=llm, prompt=prompt):
    """
    Given a question, generate a response using a RAG LLM which retrieves documents from a vectorstore and attempts
    to answer the question from the context provided by those documents
    """
    rag_chain = prompt | llm | StrOutputParser()
    docs = retriever.invoke(question)
    generation = rag_chain.invoke({"context": docs, "question": question})
    logger.debug(generation)
    return generation


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
