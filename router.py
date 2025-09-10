from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
import os

# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

def initialize_question_router(groq_api_key: str = None, model_name: str = "Gemma2-9b-It"):
    """
    Initialize a question router that determines whether to use vectorstore or wikipedia search.
    
    Args:
        groq_api_key (str): GROQ API key. If None, will try to get from environment variable.
        model_name (str): The Groq model to use. Default is "Gemma2-9b-It".
    
    Returns:
        A configured question router chain.
    """
    # Set up API key
    if groq_api_key:
        os.getenv["GROQ_API_KEY"] = groq_api_key
    elif "GROQ_API_KEY" not in os.environ:
        raise ValueError("GROQ_API_KEY not found. Please provide it as an argument or set it as an environment variable.")
    
    # Initialize LLM
    llm = ChatGroq(model_name=model_name)
    
    # Create structured LLM router
    structured_llm_router = llm.with_structured_output(RouteQuery)
    
    # Prompt
    system = """You are a routing expert for gaming customer support questions.

    VECTORSTORE (Use for these topics):
    - Game key activation/redemption issues
    - Account login and authentication problems
    - Purchase, payment, and refund inquiries
    - Technical support for gaming platforms
    - CDKeys-specific support questions
    - Platform support (Xbox, PlayStation, Steam, Epic, Nintendo, Battle.net, EA)

    WEB SEARCH (Use for these topics):
    - General gaming news and reviews
    - Game content, walkthroughs, or story questions
    - Hardware recommendations and reviews
    - Unrelated non-gaming topics
    - Very recent events not in documentation

    The vectorstore contains official support documentation from all major gaming platforms.
    Default to vectorstore for any gaming support-related questions."""
        
    route_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{question}"),
    ])
    
    # Create the router chain
    question_router = route_prompt | structured_llm_router
    
    return question_router



