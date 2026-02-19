def generate_fix(state):
    repo_path = state["repo_path"]
    file_path = f"{repo_path}/test_app.py"

    with open(file_path, "w") as f:
        f.write(
            "from app import add\n\n"
            "def test_add():\n"
            "    assert add(2, 2) == 4\n"
        )

    return state
