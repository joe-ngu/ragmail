<h1 align="center">
  <br>
  <a href="https://github.com/joe-ngu/ragmail"><img src="https://raw.githubusercontent.com/joe-ngu/ragmail/main/assets/ragmail_logo.jpeg" alt="Ragmail" width="200"></a>
  <br>
  Ragmail
  <br>
</h1>

<h4 align="center">A Retrieval-Augmented Generation (RAG) AI assistant designed to draft email responses</h4>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
  </a>
  <a href="https://www.langchain.com"/>
    <img src="https://img.shields.io/badge/langchain-%230D1C49.svg?style=for-the-badge&logo=langchain&logoColor=white" alt="Langchain"/>
  </a>
  <a href="https://www.trychroma.com/">
      <img src="https://img.shields.io/badge/chromadb-%2381D4FA.svg?style=for-the-badge&logo=&logoColor=white
" alt="ChromaDB"/>
  </a>
  <a href="https://llama.meta.com/">
    <img src="https://img.shields.io/badge/Llama%203-%231877F2.svg?style=for-the-badge
" alt="Llama 3"/>
  </a>
  <a href="https://developers.google.com/gmail/api/guides">
    <img src="https://img.shields.io/badge/Gmail-%23D14836.svg?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#quickstart">Quick Start</a> •
  <a href="#design">Design</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

- **AI-Powered by Llama 3**  
  - Llama 3 is an advanced open-source Large Language Model (LLM) developed by Meta, enabling powerful natural language processing capabilities.

- **Seamless Gmail API Integration**
  - Utilizes Google's official Gmail API to access inbox messages and compose draft responses.
  - Incorporates OAuth authentication to ensure secure user consent and transparency about the data being accessed.

- **RAG (Retrieval-Augmented Generation) Architecture**  
  - Enhances response accuracy by allowing the LLM to reference relevant user-provided information.
  - Relevant documents are stored in ChromaDB, a high-performance vector database.
  - Includes answer grading mechanisms to improve response precision and mitigate hallucinations.

- **Modular and Extensible Design**  
  - Built with LangChain, a flexible framework that allows for easy swapping of various LLMs and vector stores, ensuring adaptability to future needs.

## Quickstart

To clone and run this application, ensure you have [Git](https://git-scm.com) and [Python](https://www.python.org/downloads/) installed on your machine.

### Pre-requisites

1. **TAVILY API Key**:  
   - Sign up for a free API key at [Tavily](https://tavily.com/).
   - Create a `.env` file in the root directory of the project and add your `TAVILY_API_KEY` to it.

2. **Gmail API Credentials**:  
   - Obtain your own `credentials.json` by following the steps [here](https://developers.google.com/gmail/api/quickstart/python).
   - Place the `credentials.json` file in the `service` folder of the project.

### Setup

After completing the pre-requisites, follow these steps in your command line:


```bash
# Clone this repository
$ git clone https://github.com/joe-ngu/ragmail.git

# Navigate into the repository
$ cd ragmail

# Create and activate a virtual environment (optional but recommended)
$ python3 -m venv venv
$ source venv/bin/activate

# Install required packages
$ pip install -r requirements.txt

# Run the quickstart script
$ make quickstart
```

## Design

### Application Architecture

This application is built with a modern, scalable architecture designed to meet current requirements and accommodate future growth:

- **Backend**: The backend is driven by a RAG LLM that leverages relevant user-provided data for generating responses. When the data is insufficient, the LLM can initiate a web search using Tavily.

- **Gmail Integration**: The application integrates with the Gmail API to read inbox messages and compose draft responses in real-time.

- **Database**: ChromaDB, a vector database, stores the relevant information. The application currently supports PDF and Markdown document loaders, with a modular design allowing for easy integration of additional loaders as needed.

The following diagram illustrates the application architecture (credit to [LangGraph](https://github.com/langchain-ai/langgraph) for the diagram):

![LangGraph Design](https://raw.githubusercontent.com/joe-ngu/ragmail/main/assets/langgraph_diagram.png)

## Credits

This project was developed using knowledge gained from working with my Capstone team, mentors, and the Generative Security Applications class. Check them out here:

- **[Capstone Team](https://github.com/poojasounder/Automated-Gmail-Responder)** 
- **[Generative Security App Class](https://github.com/wu4f/cs410g-src)**
- **[LangGraph Repo](https://github.com/langchain-ai/langgraph)**


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.