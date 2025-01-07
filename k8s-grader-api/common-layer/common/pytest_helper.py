import shutil
import pytest
from enum import Enum
import urllib.request


class GamePhase(Enum):
    SETUP = "setup"
    CHECK = "check"
    CLEANUP = "cleanup"


def run_tests(test_phase: GamePhase, game: str, task: str):
    url = "https://github.com/wongcyrus/k8s-game-rule/archive/refs/heads/main.zip"
    urllib.request.urlretrieve(url, "/tmp/k8s-game-rule-main.zip")
    shutil.unpack_archive('/tmp/k8s-game-rule-main.zip', '/tmp/')
    return pytest.main(["--html=/tmp/report.html", "-x", f"/tmp/k8s-game-rule-main/k8s-tests/{test_phase.value}/{game}/{task}"])
