from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    repo_url: str
    repo_path: str
    team_name: str
    leader_name: str

    ci_logs: Optional[str]
    failures: List[str]

    iteration: int
    max_iterations: int
    passed: bool
