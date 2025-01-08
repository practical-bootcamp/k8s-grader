import json
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
    if not os.path.exists("/tmp/k8s-game-rule-main.zip"):
        url = "https://github.com/wongcyrus/k8s-game-rule/archive/refs/heads/main.zip"
        urllib.request.urlretrieve(url, "/tmp/k8s-game-rule-main.zip")
        shutil.unpack_archive('/tmp/k8s-game-rule-main.zip', '/tmp/')


def get_tasks(game: str):
    get_tests()
    folder = f"{TEST_BASE_PATH}{GamePhase.SETUP.value}/{game}/"
    tasks = []
    for file in os.listdir(folder):
        if file.endswith(".md"):
            tasks.append(file.replace("test_", "").replace(".md", ""))
    return tasks


def get_session_template(game: str, task: str):
    get_tests()
    session = {}
    game_session_file = f"{TEST_BASE_PATH}{GamePhase.SETUP.value}/{game}/session.json"
    task_session_file = f"{TEST_BASE_PATH}{GamePhase.SETUP.value}/{game}/test_{task}.json"
    if os.path.exists(game_session_file):
        with open(game_session_file, 'r', encoding='utf-8') as file:
            game_session = json.load(file)
            session.update(game_session)
    if os.path.exists(task_session_file):
        with open(task_session_file, 'r', encoding='utf-8') as file:
            task_session = json.load(file)
            session.update(task_session)

    return session


def get_current_task(game, finished_tasks):
    all_tasks = get_tasks(game)
    current_task = None
    for task in all_tasks:
        if task not in [task for task in finished_tasks]:
            current_task = task
            break
    return current_task
