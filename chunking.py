import cassio
from dotenv import load_dotenv
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.cassandra import Cassandra

def initialize_and_populate_vectorstore():
    """
    Initialize Astra DB connection and populate vector store with gaming support documentation.
    
    Returns:
        tuple: (astra_vector_store, astra_vector_index, retriever)
    """
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
    urls = [
        "https://support.cdkeys.com/",
        "https://support.xbox.com/",
        "https://www.playstation.com/en-us/support/",
        "https://help.steampowered.com/",
        "https://www.epicgames.com/help/",
        "https://en-americas-support.nintendo.com/",
        "https://us.battle.net/support/en/",
        "https://help.ea.com/en/"
    ]
    
    # Load documents
    print("Loading documents from URLs...")
    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]
    
    # Split documents
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=100
    )
    doc_splits = text_splitter.split_documents(docs_list)
    
    # Initialize embeddings
    print("Initializing embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Astra vector store
    print("Initializing Astra vector store...")
    astra_vector_store = Cassandra(
        embedding=embeddings,
        table_name="mini_demo",
        session=None,
        keyspace=None
    )
    
    # Add documents to vector store
    print("Adding documents to vector store...")
    astra_vector_store.add_documents(doc_splits)
    print(f"Inserted {len(doc_splits)} document chunks.")
    
    # Create index and retriever
    astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
    retriever = astra_vector_store.as_retriever()
    
    print("Vector store initialization complete!")
    return retriever
    

# Example usage:
if __name__ == "__main__":
    try:
        vector_store, index, retriever = initialize_and_populate_vectorstore()
        print("Successfully initialized and populated the vector store!")
        
        # You can now use these objects for querying:
        # results = retriever.get_relevant_documents("your query here")
        # print(results)
        
    except Exception as e:
        print(f"Error initializing vector store: {e}")