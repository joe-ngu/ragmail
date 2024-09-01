from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from config import settings
import logging

logger = logging.getLogger(__name__)

llm = ChatOllama(model=settings.LLM_MODEL, format="json", temperature=0)

prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an expert at routing a 
    user question to a vectorstore or web search. Use the vectorstore for questions on cybersecurity, software vulnerabilities 
    such as buffer overflow, and adversarial attacks such as phishing. You do not need to be stringent with the keywords 
    in the question related to these topics. Otherwise, use web-search. Give a binary choice 'web_search' 
    or 'vectorstore' based on the question. Return the a JSON with a single key 'datasource' and no premable or explanation. 
    Question to route: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)


def route(question, llm=llm, prompt=prompt):
    """
    Given the question and routes the to the appropriate datasource based on the question's subject matter.
    Questions pertain to cybersecurity and software vulnerabilities are answerable from the documents loaded
    in by the RAG application, all other questions will be answered via web sesarch.
    """
    question_router = prompt | llm | JsonOutputParser()
    source = question_router.invoke({"question": question})
    logger.debug(source)
    return source
