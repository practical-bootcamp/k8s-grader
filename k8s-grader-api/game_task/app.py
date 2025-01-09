import json
import logging
import os
from datetime import datetime

from common.database import (
    get_email_from_event,
    get_game_session,
    get_tasks_by_email_and_game,
    get_user_data,
    save_game_session,
)
from common.file import clear_tmp_directory, create_json_input, write_user_files
from common.pytest import (
    GamePhase,
    TestResult,
    get_current_task,
    get_instruction,
    run_tests,
)
from common.s3 import generate_presigned_url, upload_test_result
from common.session import generate_session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


os.environ["PATH"] += os.pathsep + "/opt/kubectl/"
os.environ["PATH"] += os.pathsep + "/opt/helm/"


def lambda_handler(event, context):

    email = get_email_from_event(event)
    game = event.get("queryStringParameters", {}).get("game")
    if not email or not game:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"status": "Error", "message": "Email and Game parameter is missing"}
            ),
        }

    finished_tasks = get_tasks_by_email_and_game(email, game)
    current_task = get_current_task(game, finished_tasks)
    logger.info(current_task)
    if not current_task:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "OK", "message": "All tasks are completed"}),
        }

    user_data = get_user_data(email)
    if not user_data:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"status": "Error", "message": "Email not found in the database"}
            ),
        }
    client_certificate = user_data.get("client_certificate")
    client_key = user_data.get("client_key")
    endpoint = user_data.get("endpoint")

    if not all([client_certificate, client_key, endpoint]):
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"status": "Error", "message": "K8s confdential is missing"}
            ),
        }
    clear_tmp_directory()
    write_user_files(client_certificate, client_key)

    instruction = None
    session = get_game_session(email, game, current_task)
    if session is None:
        session = generate_session(email, game, current_task)
        instruction = get_instruction(game, current_task, session)
        if not instruction:
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"status": "Error", "message": "Instruction not found!"}
                ),
            }
    else:
        instruction = session["$instruction"]
    session["$instruction"] = instruction
    session["$client_certificate"] = client_certificate
    session["$client_key"] = client_key
    session["$endpoint"] = endpoint
    save_game_session(email, game, current_task, session)
    logger.info(session)

    try:
        create_json_input(endpoint, session)
        test_result = run_tests(GamePhase.SETUP, game, current_task)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upload_test_result(
            "/tmp/report.html", GamePhase.CHECK, now_str, email, game, current_task
        )
        report_url = generate_presigned_url(
            GamePhase.CHECK, now_str, email, game, current_task
        )

    except Exception as e:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"status": "Error", "message": f"{type(e).__name__}: {str(e)}"}
            ),
        }

    if test_result == TestResult.OK:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": test_result.name,
                    "message": instruction,
                    "report_url": report_url,
                }
            ),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "status": test_result.name,
                "message": "Something is wrong!",
                "report_url": report_url,
            }
        ),
    }
