import cassio
from dotenv import load_dotenv
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import Cassandra

# Global variable to store the initialized retriever
retriever = None

def initialize_and_populate_vectorstore():
    """
    Initialize Astra DB connection and populate vector store with gaming support documentation.
    Returns the retriever (initializes only once).
    """
    global retriever
    
    # If already initialized, return the retriever
    if retriever is not None:
        print("---USING EXISTING VECTOR STORE---")
        return retriever
    
    print("---INITIALIZING VECTOR STORE (FIRST TIME)---")
    # Load environment variables
    load_dotenv()
    
    # Get values from environment variables
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
    
    # Verify the values are loaded
    if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_ID:
        raise ValueError("Missing required environment variables: ASTRA_DB_APPLICATION_TOKEN and ASTRA_DB_ID")
    
    print(f"Token loaded: {bool(ASTRA_DB_APPLICATION_TOKEN)}")
    print(f"DB ID loaded: {bool(ASTRA_DB_ID)}")
    
    # Initialize Cassandra connection
    cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)
    
    # URLs to scrape
    print("Loading documents from local repository...")
    
    # Method 1: If you have text files in a directory
    loader = DirectoryLoader(
        path="./data/",
        glob="**/*.txt",  # or "**/*.html" 
        loader_cls=TextLoader,
        show_progress=True
    )
    docs_list = loader.load()
    
    # Split documents - INCREASED CHUNK SIZE
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,  # Increased from 400
        chunk_overlap=100  # Increased overlap
    )
    doc_splits = text_splitter.split_documents(docs_list)
    
    # Initialize embeddings
    print("Initializing embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Astra vector store
    print("Initializing Astra vector store...")
    astra_vector_store = Cassandra(
        embedding=embeddings,
        table_name="test11",
        session=None,
        keyspace=None
    )
    
    # Add documents to vector store
    print("Adding documents to vector store...")
    astra_vector_store.add_documents(doc_splits)
    print(f"Inserted {len(doc_splits)} document chunks.")
    
    # Create retriever with better search
    retriever = astra_vector_store.as_retriever(search_kwargs={"k": 5})
    
    print("Vector store initialization complete!")
    return retriever