from fastapi import APIRouter
from app.schemas.request import RunAgentRequest
from app.agent.graph import run_agent_graph

router = APIRouter()

# @router.post("/run-agent")
# def run_agent(payload: RunAgentRequest):
#     result = run_agent_graph(payload)
#     return result


@router.post("/run-agent")
def run_agent(payload: RunAgentRequest):
    result = run_agent_graph.invoke({
        "repo_url": str(payload.repo_url),
    "repo_path": "",
    "team_name": payload.team_name,
    "leader_name": payload.leader_name,
    "ci_logs": payload.ci_logs,
    "failures": [],
    "iteration": 0,
    "max_iterations": 3,
    "passed": False
    })
    return result