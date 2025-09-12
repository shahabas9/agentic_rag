# test_workflow.py
from compile import build_workflow

app = build_workflow()

def run_query(question: str):
    state = {"question": question, "generation": "", "documents": []}
    result = app.invoke(state)
    
    print("\n=== FINAL ANSWER ===")
    # Extract just the answer content for the user
    if hasattr(result['generation'], 'content'):
        print(result['generation'].content)
    else:
        print(result['generation'])
    
    # print("\n=== INTERNAL STATE (debug) ===")
    # print(result)

if __name__ == "__main__":
    
    run_query("Which currencies do you accept??")
    
    run_query("How can I change my email for my order delivery?")