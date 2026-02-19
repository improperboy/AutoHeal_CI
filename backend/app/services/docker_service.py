import docker
import os
from docker.errors import ContainerError, DockerException

def run_tests(repo_path: str):
    """
    Run tests inside a Docker container.
    Returns (passed: bool, logs: str)
    """

    try:
        client = docker.from_env()

        output = client.containers.run(
            image="python:3.11-slim",
            command=(
                "sh -c "
                "'pip install -r requirements.txt || true && "
                "pytest || python -m unittest'"
            ),
            volumes={
                os.path.abspath(repo_path): {
                    "bind": "/repo",
                    "mode": "rw"
                }
            },
            working_dir="/repo",
            stderr=True,
            stdout=True,
            remove=True
        )

        return True, output.decode()

    except ContainerError as e:
        return False, e.stderr.decode() if e.stderr else str(e)

    except DockerException as e:
        return False, f"Docker error: {str(e)}"
