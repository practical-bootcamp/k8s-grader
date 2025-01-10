import json
import logging
from datetime import datetime

from common.database import (
    delete_game_session,
    get_email_from_event,
    get_game_session,
    get_tasks_by_email_and_game,
    get_user_data,
    save_game_task,
)
from common.file import clear_tmp_directory, create_json_input, write_user_files
from common.handler import error_response, setup_paths
from common.pytest import GamePhase, TestResult, get_current_task, run_tests
from common.s3 import generate_presigned_url, upload_test_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


setup_paths()


def lambda_handler(event, context):

    email = get_email_from_event(event)
    game = event.get("queryStringParameters", {}).get("game")
    if not email or not game:
        return error_response("Email and Game parameter is missing")

    if not game.isalnum():
        return error_response("Game parameter must be a single alphanumeric word")

    user_data = get_user_data(email)
    if not user_data:
        return error_response("Email not found in the database")

    client_certificate = user_data.get("client_certificate")
    client_key = user_data.get("client_key")
    endpoint = user_data.get("endpoint")

    if not all([client_certificate, client_key, endpoint]):
        return error_response("K8s confdential is missing.")

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
    if session is None:
        return error_response("Session not found, and no ongoing task.")
    logger.info(session)

    # In case the key or endpoint is changed, remove the session.
    required_keys = ["$endpoint", "$client_key", "$client_certificate"]
    for key in required_keys:
        if session[key] != locals()[key[1:]]:
            delete_game_session(email, game, current_task)
            return error_response("Cluster setting is difference from setup!")

    try:
        create_json_input(endpoint, session)
        test_result = run_tests(GamePhase.CHECK, game, current_task)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upload_test_result(
            "/tmp/report.html", GamePhase.CHECK, now_str, email, game, current_task
        )
        report_url = generate_presigned_url(
            GamePhase.CHECK, now_str, email, game, current_task
        )

        if test_result == TestResult.OK:
            save_game_task(email, game, current_task)
            run_tests(GamePhase.CLEANUP, game, current_task)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            upload_test_result(
                "/tmp/report.html",
                GamePhase.CLEANUP,
                now_str,
                email,
                game,
                current_task,
            )
    except Exception as e:
        return error_response(f"{type(e).__name__}: {str(e)}")

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
