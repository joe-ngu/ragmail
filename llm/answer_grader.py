import logging
from config import settings

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

llm = ChatOllama(model=settings.LLM_MODEL, format="json", temperature=0)

prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an 
    answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is 
    useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
     <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
    \n ------- \n
    {generation} 
    \n ------- \n
    Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "question"],
)


def grade_answer(question, generation, llm=llm, prompt=prompt):
    """
    Grades whether the answer generated answers the question asked by the user.
    Returns "yes" if the answer is relevant to the question and "no" otherwise.
    """
    answer_grader = prompt | llm | JsonOutputParser()
    score = answer_grader.invoke({"question": question, "generation": generation})
    logger.debug(score)
    return score["score"]
