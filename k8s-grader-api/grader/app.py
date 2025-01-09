import json
import logging
import os
from datetime import datetime

from common.database import (
    get_email_from_event,
    get_game_session,
    get_tasks_by_email_and_game,
    get_user_data,
    save_game_task,
)
from common.file import clear_tmp_directory, create_json_input, write_user_files
from common.pytest import GamePhase, TestResult, get_current_task, run_tests
from common.s3 import generate_presigned_url, upload_test_result

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
                {"status": "Error", "message": "K8s confdential is missing."}
            ),
        }
    clear_tmp_directory()
    write_user_files(client_certificate, client_key)

    finished_tasks = get_tasks_by_email_and_game(email, game)
    current_task = get_current_task(game, finished_tasks)
    logger.info(current_task)
    if not current_task:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "OK", "message": "All tasks are completed"}),
        }
    session = get_game_session(email, game, current_task)

    required_keys = ["$endpoint", "$client_key", "$client_certificate"]
    for key in required_keys:
        if session[key] != locals()[key[1:]]:
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"status": "Error", "message": "Cluster setting is not the same!"}
                ),
            }

    if session is None:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "Error", "message": "Session not found"}),
        }
    logger.info(session)

    try:
        create_json_input(endpoint, session)
        test_result = run_tests(GamePhase.CHECK, game, current_task)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upload_test_result("/tmp/report.html", now_str, email, game, current_task)
        report_url = generate_presigned_url(now_str, email, game, current_task)

        if test_result == TestResult.OK:
            save_game_task(email, game, current_task)
            run_tests(GamePhase.CLEANUP, game, current_task)
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
                    "message": "Task Completed!",
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
