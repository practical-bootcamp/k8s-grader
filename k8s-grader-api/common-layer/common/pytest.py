import json
import os
import shutil
import threading
import urllib.request

import pytest
from common.database import get_game_source
from common.status import GamePhrase, TestResult
from jinja2 import Environment

MAPPING = {
    GamePhrase.SETUP: "01_setup",
    GamePhrase.READY: "02_ready",
    GamePhrase.ANSWER: "03_answer",
    GamePhrase.CHALLENGE: "04_challenge",
    GamePhrase.CHECK: "05_check",
    GamePhrase.CLEANUP: "06_cleanup",
}

GAME_PHRASE_ORDER = [
    GamePhrase.SETUP,
    GamePhrase.READY,
    GamePhrase.CHALLENGE,
    GamePhrase.CHECK,
    GamePhrase.CLEANUP,
]


def get_root_path(game: str) -> str:
    return f"/tmp/{game}"


def get_test_base_path(game: str) -> str:
    return f"/tmp/{game}/tests"


def run_tests(test_phase: GamePhrase, game: str, task: str):
    get_tests(game)

    def run_pytest():
        nonlocal retcode
        retcode = pytest.main(
            [
                f"--rootdir={get_root_path(game)}",
                "--import-mode=importlib",
                "--html=/tmp/report.html",
                "--self-contained-html",
                "-x",
                f"{get_test_base_path(game)}/{game}/{task}/test_{MAPPING[test_phase]}.py",
            ]
        )

    retcode = TestResult.OK.value
    thread = threading.Thread(target=run_pytest)
    thread.start()
    thread.join(timeout=25)

    if thread.is_alive():
        retcode = TestResult.TIME_OUT.value
    return TestResult(retcode)


def get_repo_branch(game: str) -> tuple[str, str]:
    source = get_game_source(game)
    if source.startswith("https://github.com/"):
        parts = source.split("/")
        repo = parts[-3]
        branch = parts[-1].replace(".zip", "").split("/")[-1]
        return repo, branch
    return None, None


def get_tests(game: str):
    source = get_game_source(game)
    distination = f"/tmp/{game}.zip"
    if not os.path.exists(distination):
        urllib.request.urlretrieve(source, distination)
        shutil.unpack_archive(distination, "/tmp/")
        repo, branch = get_repo_branch(game)
        source_folder = repo + "-" + branch
        shutil.move(f"/tmp/{source_folder}", get_root_path(game))


def get_tasks(game: str):
    get_tests(game)
    folder = f"{get_test_base_path(game)}/{game}/"
    tasks = []
    for file in sorted(os.listdir(folder)):
        if os.path.isdir(os.path.join(folder, file)) and "99_test_template" not in file:
            tasks.append(file)
    return tasks


def get_session_template(game: str, task: str):
    get_tests(game)
    session = {}
    game_session_file = f"{get_test_base_path(game)}/{game}/session.json"
    task_session_file = f"{get_test_base_path(game)}/{game}/{task}/session.json"
    if os.path.exists(game_session_file):
        with open(game_session_file, "r", encoding="utf-8") as file:
            game_session = json.load(file)
            session.update(game_session)
    if os.path.exists(task_session_file):
        with open(task_session_file, "r", encoding="utf-8") as file:
            task_session = json.load(file)
            session.update(task_session)

    return session


def get_current_task(game: str, finished_tasks):
    all_tasks = get_tasks(game)
    current_task = None
    for task in all_tasks:
        if task not in [task for task in finished_tasks]:
            current_task = task
            break
    return current_task


def render(template, session):
    env = Environment()
    jinja_template = env.from_string(template)
    template_string = jinja_template.render(session)
    return template_string


def get_instruction(game: str, task: str, session: dict):
    get_tests(game)
    instructions_file = f"{get_test_base_path(game)}/{game}/{task}/instruction.md"

    if os.path.exists(instructions_file):
        with open(instructions_file, "r", encoding="utf-8") as file:
            instruction = file.read()
        return render(instruction, session)
    return None


def get_ai_instruction(instruction: str, session: dict):
    return render(instruction, session)


def get_next_game_phrase(game: str, task: str, current_game_phrase: GamePhrase):
    get_tests(game)

    current_index = GAME_PHRASE_ORDER.index(current_game_phrase)
    for next_index in range(current_index + 1, len(GAME_PHRASE_ORDER)):
        test_file = f"{get_test_base_path(game)}/{game}/{task}/test_{MAPPING[GAME_PHRASE_ORDER[next_index]]}.py"
        if os.path.exists(test_file):
            return GAME_PHRASE_ORDER[next_index]
    return None
