from langchain.schema import Document
from chunking import initialize_and_populate_vectorstore
from langchain_community.tools import DuckDuckGoSearchResults
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

web_search_tool = DuckDuckGoSearchResults()



def format_docs(docs):
    """Format documents into a single string for context."""
    if not docs:
        return "No relevant documents found."
    
    if hasattr(docs, 'page_content'):
        # Single document
        return docs.page_content
    elif isinstance(docs, list) and docs and hasattr(docs[0], 'page_content'):
        # List of documents
        return "\n\n".join([doc.page_content for doc in docs])
    else:
        return str(docs)


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]
    retriever = initialize_and_populate_vectorstore()
    # Retrieval
    documents = retriever.invoke(question,search_kwargs={"k": 5})
    print(f"Retrieved {len(documents)} documents for: {question}")
    for i, doc in enumerate(documents):
        print(f"Doc {i+1}: {doc.page_content[:200]}...")
    return {"documents": documents, "question": question}


def web_search(state):
    """
    Web search based on the re-phrased question.
    """
    print("---WEB SEARCH---")
    question = state["question"]
    
    # Web search with concise results
    docs = web_search_tool.invoke({"query": question, "max_results": 3})
    
    # Format web results properly
    if docs and isinstance(docs, list):
        # Extract just the snippets
        web_content = "\n".join([doc.get('snippet', '') for doc in docs[:2]])
    else:
        web_content = str(docs)
    
    web_results = Document(page_content=web_content)

    return {"documents": web_results, "question": question}

def generate(state):
    """
    LangGraph node: generate a professional, concise answer based on question and retrieved documents.

    Args:
        state (dict): Current graph state, must contain 'question' and 'documents'

    Returns:
        dict: Updated state with a new key 'generation' containing the generated answer
    """
    print("---GENERATE ANSWER NODE---")
    
    question = state.get("question", "")
    documents = state.get("documents", [])

    # Format documents into plain text for RAG/LLM
    docs_txt = format_docs(documents)

    # Create a proper ChatPromptTemplate (not a string)
    prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a Loaded (formerly CDKeys) customer support agent. Provide clear, helpful answers.

        GUIDELINES:
        - Be concise but complete (2-4 sentences)
        - Use professional but friendly tone  
        - Focus on solving the customer's issue
        - If you don't know, say so politely"""),
            ("human", """CONTEXT: {context}

        CUSTOMER QUESTION: {question}

        Please provide a helpful response:""")
        ])
    
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")  # Note: should be GROQ_API_KEY, not groq_api_key
    
    # Set up API key
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    elif "GROQ_API_KEY" not in os.environ:
        raise ValueError("GROQ_API_KEY not found. Please provide it as an argument or set it as an environment variable.")
    
    # Initialize LLM
    llm = ChatGroq(model_name="llama-3.1-8b-instant")
    
    # Create the chain properly
    rag_chain = prompt_template | llm
    
    # Invoke the chain with the correct input format
    generation = rag_chain.invoke({"context": docs_txt, "question": question})
    
    return {"documents": documents, "question": question, "generation": generation}

