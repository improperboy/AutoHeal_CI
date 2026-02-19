import os
import tempfile
from git import Repo

def clone_repo(state):
    tmp_dir = tempfile.mkdtemp()
    Repo.clone_from(state["repo_url"], tmp_dir)

    branch = f"{state['team_name']}_{state['leader_name']}_AI_Fix"

    state["repo_path"] = tmp_dir
    state["branch_name"] = branch
    state["iteration"] = 0

    return state
