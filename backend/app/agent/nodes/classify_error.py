# def classify_error(state):
#     state["failures"].append({
#         "file": "example.py",
#         "line": 1,
#         "type": "SYNTAX"
#     })
#     return state

def classify_error(state):
    logs = state.get("ci_logs", "")

    if "AssertionError" in logs:
        state["failures"] = ["AssertionError in tests"]
    else:
        state["failures"] = ["Unknown failure"]

    return state
