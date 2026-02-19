# # from langgraph.graph import StateGraph, END
# # from app.agent.state import AgentState
# # from app.agent.nodes.clone_repo import clone_repo
# # from app.agent.nodes.run_tests import run_tests
# # from app.agent.nodes.classify_error import classify_error
# # from app.agent.nodes.generate_fix import generate_fix
# # from app.agent.nodes.commit_fix import commit_fix
# # from app.agent.nodes.rerun_ci import rerun_ci

# # def run_agent_graph(payload):
# #     graph = StateGraph(AgentState)

# #     graph.add_node("clone_repo", clone_repo)
# #     graph.add_node("run_tests", run_tests)
# #     graph.add_node("classify_error", classify_error)
# #     graph.add_node("generate_fix", generate_fix)
# #     graph.add_node("commit_fix", commit_fix)
# #     graph.add_node("rerun_ci", rerun_ci)

# #     graph.set_entry_point("clone_repo")

# #     graph.add_edge("clone_repo", "run_tests")

# #     graph.add_conditional_edges(
# #         "run_tests",
# #         lambda state: "passed" if state["passed"] else "classify_error",
# #         {
# #             "passed": END,
# #             "classify_error": "classify_error"
# #         }
# #     )

# #     graph.add_edge("classify_error", "generate_fix")
# #     graph.add_edge("generate_fix", "commit_fix")
# #     graph.add_edge("commit_fix", "rerun_ci")
# #     graph.add_edge("rerun_ci", "run_tests")

# #     compiled = graph.compile()

# #     initial_state: AgentState = {
# #         "repo_url": payload.repo_url,
# #         "repo_path": "",
# #         "team_name": payload.team_name.upper().replace(" ", "_"),
# #         "leader_name": payload.leader_name.upper().replace(" ", "_"),
# #         "branch_name": "",
# #         "failures": [],
# #         "iteration": 0,
# #         "max_iterations": 5,
# #         "passed": False
# #     }

# #     return compiled.invoke(initial_state)



# from langgraph.graph import StateGraph, END
# from app.agent.state import AgentState

# from app.agent.nodes.clone_repo import clone_repo
# from app.agent.nodes.run_tests import run_tests
# from app.agent.nodes.classify_error import classify_error
# from app.agent.nodes.generate_fix import generate_fix
# from app.agent.nodes.commit_fix import commit_fix

# def should_continue(state: AgentState):
#     if state["passed"]:
#         return END
#     if state["iteration"] >= state["max_iterations"]:
#         return END
#     return "generate_fix"

# builder = StateGraph(AgentState)

# builder.add_node("clone_repo", clone_repo)
# builder.add_node("run_tests", run_tests)
# builder.add_node("classify_error", classify_error)
# builder.add_node("generate_fix", generate_fix)
# builder.add_node("commit_fix", commit_fix)

# builder.set_entry_point("clone_repo")

# builder.add_edge("clone_repo", "run_tests")
# builder.add_edge("run_tests", "classify_error")
# builder.add_edge("classify_error", "generate_fix")
# builder.add_edge("generate_fix", "commit_fix")
# builder.add_edge("commit_fix", "run_tests")

# builder.add_conditional_edges(
#     "run_tests",
#     should_continue
# )

# run_agent_graph = builder.compile()


from langgraph.graph import StateGraph, END
from app.agent.state import AgentState

from app.agent.nodes.clone_repo import clone_repo
from app.agent.nodes.run_tests import run_tests
from app.agent.nodes.classify_error import classify_error
from app.agent.nodes.generate_fix import generate_fix
from app.agent.nodes.commit_fix import commit_fix


def after_tests(state: AgentState):
    if state["passed"]:
        return END
    if state["iteration"] >= state["max_iterations"]:
        return END
    return "classify_error"


builder = StateGraph(AgentState)

builder.add_node("clone_repo", clone_repo)
builder.add_node("run_tests", run_tests)
builder.add_node("classify_error", classify_error)
builder.add_node("generate_fix", generate_fix)
builder.add_node("commit_fix", commit_fix)

builder.set_entry_point("clone_repo")

builder.add_edge("clone_repo", "run_tests")

# 👇 IMPORTANT: Remove the normal edge from run_tests
# builder.add_edge("run_tests", "classify_error") ❌ DELETE THIS

builder.add_conditional_edges(
    "run_tests",
    after_tests
)

builder.add_edge("classify_error", "generate_fix")
builder.add_edge("generate_fix", "commit_fix")
builder.add_edge("commit_fix", "run_tests")

run_agent_graph = builder.compile()
