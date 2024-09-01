import logging
from typing import List
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph
from langchain_core.documents import Document

from database.vectorstore import retriever

from llm.retrieval_grader import grade_retrieval
from llm.rag import generate_response
from llm.hallucination_grader import grade_hallucination
from llm.answer_grader import grade_answer
from llm.router import route

from config import setup_logging
from llm.tools import web_search_tool

setup_logging("langgraph_svc")
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """
    Represents the state of the graph with the following properties:
    - question: the question to answer
    - generation: the response generated by the LLM
    - web_search: whether to use the search tool
    - documents: list of documents retrieved by the rag application
    """

    question: str
    generation: str
    web_search: str
    documents: List[str]


def retrieve(state):
    """
    Retrieve documents from vectorstore and add documents to graph state
    """
    logger.info("---RETRIEVING DOCUMENTS---")
    question = state["question"]

    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}


def generate(state):
    """
    Generate answer using RAG on retrieved documents and add generation to graph state
    """
    logger.info("---GENERATING RESPONSE---")
    question = state["question"]
    documents = state["documents"]

    generation = generate_response(question=question)
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, set a flag to run web search
    """

    logger.info("---CHECKING DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = "No"
    for d in documents:
        grade = grade_retrieval(question=question, document=d.page_content)
        if grade.lower() == "yes":
            logger.info("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:  # Document not relevant
            logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = "Yes"
    return {"documents": filtered_docs, "question": question, "web_search": web_search}


def web_search(state):
    """
    Web search based on the question and add results to documents of graph's current state
    """
    logger.info("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
    return {"documents": documents, "question": question}


def route_question(state):
    """
    Given the current graph state, route question to web search or RAG.
    Returns the next node to call.
    """
    logger.info("---ROUTE QUESTION---")
    question = state["question"]
    logger.debug(f"Question: {question}")
    source = route(question=question)
    logger.debug(source)

    if source["datasource"] == "web_search":
        logger.info("---ROUTE QUESTION TO WEB SEARCH---")
        return "websearch"
    elif source["datasource"] == "vectorstore":
        logger.info("---ROUTE QUESTION TO RAG---")
        return "vectorstore"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or add web search
    Returns decision for next node to call
    """
    logger.info("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    web_search = state["web_search"]
    state["documents"]

    if web_search == "Yes":
        logger.info(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return "websearch"
    else:
        logger.info("---DECISION: GENERATE---")
        return "generate"


def grade_generation(state):
    """
    Determines whether the generation is grounded in the document and answers question.
    Returns decision for next node to call
    """

    logger.info("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    grade = grade_hallucination(documents=documents, generation=generation)

    if grade == "yes":
        logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        logger.info("---GRADE GENERATION vs QUESTION---")
        grade = grade_answer(question=question, generation=generation)
        if grade == "yes":
            logger.info("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            logger.info("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        logger.info("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("websearch", web_search)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)

# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        "websearch": "websearch",
        "vectorstore": "retrieve",
    },
)

workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_edge("websearch", "generate")
workflow.add_conditional_edges(
    "generate",
    grade_generation,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "websearch",
    },
)
