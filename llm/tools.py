import logging
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults


logger = logging.getLogger(__name__)

load_dotenv()
web_search_tool = TavilySearchResults(max_results=3)
