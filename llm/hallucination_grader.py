import logging
from config import settings

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

llm = ChatOllama(model=settings.LLM_MODEL, format="json", temperature=0)

prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether 
    an answer is grounded in / supported by a set of facts. Give a binary 'yes' or 'no' score to indicate 
    whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a 
    single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the facts:
    \n ------- \n
    {documents} 
    \n ------- \n
    Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "documents"],
)


def grade_hallucination(documents, generation, llm=llm, prompt=prompt):
    """
    Grades whether the answer generated is grounded in the documents or facts found.
    Returns "yes" if the answer is derived from a source of truth and "no" if it is a hallucination.
    """
    hallucination_grader = prompt | llm | JsonOutputParser()
    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    logger.debug(score)
    return score["score"]
