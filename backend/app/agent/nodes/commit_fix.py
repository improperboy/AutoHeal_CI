# def commit_fix(state):
#     state["iteration"] += 1
#     return state

from git import Repo

def commit_fix(state):
    repo_path = state["repo_path"]

    repo = Repo(repo_path)
    repo.git.add(all=True)
    repo.index.commit("AutoHeal CI: Fix failing test")

    return state

