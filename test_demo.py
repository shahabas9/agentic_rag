import cassio
from dotenv import load_dotenv
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper

load_dotenv()

# Get values from environment variables, not hardcoded strings
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")

# Verify the values are loaded
print(f"Token loaded: {bool(ASTRA_DB_APPLICATION_TOKEN)}")
print(f"DB ID loaded: {bool(ASTRA_DB_ID)}")

cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)
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

# Load
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Split
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=100
)
doc_splits = text_splitter.split_documents(docs_list)


embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

from langchain.vectorstores.cassandra import Cassandra
astra_vector_store=Cassandra(
    embedding=embeddings,
    table_name="mini_demo",
    session=None,
    keyspace=None

)


astra_vector_store.add_documents(doc_splits)
print("Inserted %i headlines." % len(doc_splits))

astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)