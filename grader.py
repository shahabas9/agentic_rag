# grader.py
from langchain_groq import ChatGroq
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv
import os
import re

class GradeAnswer(BaseModel):
    grade: str = Field(description="The grade of the answer, either 'good' or 'poor'")
    reason: str = Field(description="Brief reason for the grade")

def grade_answer(state):
    """
    Evaluate the quality of the generated answer.
    """
    load_dotenv()

    print("---GRADE ANSWER---")
    answer = state.get("generation", "")
    question = state["question"]

    # Extract just the content if it's a message object
    if hasattr(answer, 'content'):
        answer_text = answer.content
    else:
        answer_text = str(answer)

    print(f"DEBUG - Answer to grade: {answer_text}")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found.")

    # Use a reliable model
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.1)
    
    # Create structured output grader
    structured_grader = llm.with_structured_output(GradeAnswer)

    grading_prompt = f"""
    Evaluate this customer support answer:

    QUESTION: {question}
    ANSWER: {answer_text}

    GRADE CRITERIA:
    - "good": Answer is helpful, accurate, and addresses the question
    - "poor": Answer is wrong, unhelpful, or avoids the question

    IMPORTANT: If the answer provides useful information that solves the customer's problem, 
    it should be graded as "good", even if it's detailed.

    Examples of "good" answers:
    - Step-by-step instructions for solving a problem
    - Clear explanations of processes
    - Helpful suggestions when exact answer isn't known
    - Professional, polite responses

    Examples of "poor" answers:
    - "I don't know" without any helpful suggestions
    - Completely wrong information
    - Rude or unprofessional tone
    - Answers that don't address the question

    Provide your grade and a brief reason.
    """
    
    try:
        result = structured_grader.invoke(grading_prompt)
        print(f"DEBUG - Grade result: {result.grade}, Reason: {result.reason}")
        
        # Ensure lowercase and clean up
        grade = result.grade.lower().strip()
        if 'good' in grade:
            final_grade = "good"
        else:
            final_grade = "poor"
            
        print(f"Final grade: {final_grade}")
        return {"grade": final_grade}
        
    except Exception as e:
        print(f"Error in grading: {e}")
        # Fallback: use simple rule-based grading
        if any(phrase in answer_text.lower() for phrase in ["i don't know", "unfortunately", "sorry", "cannot help"]):
            return {"grade": "poor"}
        else:
            return {"grade": "good"}