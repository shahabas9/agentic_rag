from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

def initialize_question_router(groq_api_key: str = None, model_name: str = "openai/gpt-oss-20b"):
    """
    Initialize a question router that determines whether to use vectorstore or wikipedia search.
    
    Args:
        groq_api_key (str): GROQ API key. If None, will try to get from environment variable.
        model_name (str): The Groq model to use. Default is "Gemma2-9b-It".
    
    Returns:
        A configured question router chain.
    """
    load_dotenv()
    groq_api_key = os.getenv("groq_api_key")
    # Set up API key
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    elif "GROQ_API_KEY" not in os.environ:
        raise ValueError("GROQ_API_KEY not found. Please provide it as an argument or set it as an environment variable.")
    
    # Initialize LLM
    llm = ChatGroq(model_name=model_name)
    
    # Create structured LLM router
    structured_llm_router = llm.with_structured_output(RouteQuery)
    
    # Prompt
    system = """You are a routing expert for Loaded (formerly CDKeys) gaming customer support.

        VECTORSTORE (Use for Loaded/gaming support questions):
        - Game key activation/redemption
        - Account login issues
        - Purchase, payment, refund questions
        - Loaded-specific support (formerly CDKeys)
        - Gaming platform support (Xbox, PlayStation, Steam, etc.)

        WEB SEARCH (Use for other topics):
        - General gaming news/reviews
        - Game content/story questions
        - Hardware recommendations
        - Non-gaming topics (weather, sports, etc.)
        - Very recent events

        Always prefer vectorstore for Loaded and gaming support questions."""
        
    route_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{question}"),
    ])
    
    # Create the router chain
    question_router = route_prompt | structured_llm_router
    
    return question_router



