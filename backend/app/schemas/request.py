# from pydantic import BaseModel, HttpUrl, Field

# class RunAgentRequest(BaseModel):
#     repo_url: HttpUrl = Field(..., description="GitHub repository URL")
#     team_name: str = Field(..., min_length=1)
#     leader_name: str = Field(..., min_length=2)

from pydantic import BaseModel, HttpUrl
from typing import Optional

class RunAgentRequest(BaseModel):
    repo_url: HttpUrl
    team_name: str
    leader_name: str
    ci_logs: Optional[str] = None
