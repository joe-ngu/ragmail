import os
import logging
from config import settings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.loader import load_data

logger = logging.getLogger(__name__)


def init_vectorstore():
    """
    Initializes a vectorstore by loading in files in the data directory as documents,
    chunking up those documents, and saving it as a Chroma vector database into local memory
    """
    documents = load_data(settings.DATA_DIR)
    docs_list = [item for sublist in documents for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    chunked_documents = text_splitter.split_documents(docs_list)

    vectorstore = Chroma.from_documents(
        documents=chunked_documents,
        persist_directory=settings.PERSIST_DIR,
        embedding=settings.EMBEDDING_MODEL,
    )
    return vectorstore


# If the vector database does not exist, initialize it
if not os.path.exists(settings.PERSIST_DIR):
    vectorstore = init_vectorstore()
# otherwise load in the vector store from local memory (avoid ingesting documents on every run)
else:
    vectorstore = Chroma(
        persist_directory=settings.PERSIST_DIR,
        embedding_function=settings.EMBEDDING_MODEL,
    )

retriever = vectorstore.as_retriever()
