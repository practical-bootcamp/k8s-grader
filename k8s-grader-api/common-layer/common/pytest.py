import shutil
import pytest
from enum import Enum
import os
import urllib.request


class GamePhase(Enum):
    SETUP = "setup"
    CHECK = "check"
    CLEANUP = "cleanup"


TEST_BASE_PATH = "/tmp/k8s-game-rule-main/k8s-tests/"


def run_tests(test_phase: GamePhase, game: str, task: str):
    get_tests()
    return pytest.main(["--html=/tmp/report.html", "-x", f"{TEST_BASE_PATH}{test_phase.value}/{game}/{task}"])


def get_tests():
    # TODO: Change this to S3 bucket download
    url = "https://github.com/wongcyrus/k8s-game-rule/archive/refs/heads/main.zip"
    urllib.request.urlretrieve(url, "/tmp/k8s-game-rule-main.zip")
    shutil.unpack_archive('/tmp/k8s-game-rule-main.zip', '/tmp/')


def get_tasks(game: str):
    folder = f"{TEST_BASE_PATH}{GamePhase.SETUP}/{game}/"
    tasks = []
    for file in os.listdir(folder):
        if file.endswith(".md"):
            tasks.append(file.replace("test_", "").replace(".md", ""))
    return tasks
