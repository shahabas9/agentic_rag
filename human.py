# human.py
def human_escalation(state):
    """
    Escalate the question to human support if LLM output is poor.
    """
    print("---ESCALATE TO HUMAN SUPPORT---")
    question = state["question"]
    documents = state.get("documents", [])
    answer = state.get("generation", "")

    # Simulate sending to human agent system
    print(f"Escalating:\nQ: {question}\nAnswer: {answer}\nDocs: {documents}")
    
    return {"generation": "Escalated to human support", "grade": "poor"}
