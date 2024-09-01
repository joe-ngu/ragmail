import logging
from pathlib import Path
from langchain_community.vectorstores.utils import filter_complex_metadata

from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredMarkdownLoader,
)

logger = logging.getLogger(__name__)


def load_pdf(file_path):
    """Given a file path, loads the pdf file and returns a list of documents"""
    logger.info(f"Loading PDF file: {file_path}")
    loader = UnstructuredPDFLoader(file_path)
    documents = loader.load()
    documents = filter_complex_metadata(documents)
    return documents


def load_markdown(file_path):
    """Given a file path, loads the markdown file and returns a list of documents"""
    logger.info(f"Loading Markdown file: {file_path}")
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()
    documents = filter_complex_metadata(documents)
    return documents


loaders = {
    ".pdf": load_pdf,
    ".md": load_markdown,
}


def load_data(directory):
    if not Path(directory).is_dir():
        raise NotADirectoryError(f"{directory} is not a valid directory")

    loaded_documents = []
    for file_path in Path(directory).iterdir():
        if file_path.is_file():
            file_extension = file_path.suffix.lower()
            loader = loaders.get(file_extension)
            if loader:
                documents = loader(str(file_path))
                loaded_documents.append(documents)
            else:
                logger.error(f"No loader available for file: {file_path}")

    return loaded_documents
