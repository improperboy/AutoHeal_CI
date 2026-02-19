import sys
import subprocess
def run_tests(state):
    repo_path = state["repo_path"]

    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=repo_path,
        capture_output=True,
        text=True
)


    output = result.stdout + result.stderr

    if result.returncode == 0:
        state["passed"] = True
        state["failures"] = []
    else:
        state["passed"] = False
        state["failures"] = [output]

    state["iteration"] += 1

    return state
