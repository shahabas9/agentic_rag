# graph.py
from typing import List
from typing_extensions import TypedDict

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: The user question
        generation: The LLM-generated answer
        documents: Retrieved documents
        grade: Evaluation of the answer (good/poor)
    """
    question: str
    generation: str
    documents: List[str]
    grade: str  # "good" or "poor"
