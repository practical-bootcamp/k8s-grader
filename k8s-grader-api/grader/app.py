import logging
from datetime import datetime

from common.database import (
    delete_game_session,
    get_game_session,
    get_tasks_by_email_and_game,
    get_user_data,
    save_game_task,
)
from common.file import clear_tmp_directory, create_json_input, write_user_files
from common.handler import (
    error_response,
    extract_k8s_credentials,
    get_email_and_game_from_event,
    ok_response,
    setup_paths,
    test_result_response,
)
from common.pytest import GamePhrase, TestResult, get_current_task, run_tests
from common.s3 import generate_presigned_url, upload_test_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


setup_paths()


def get_game_phrase(event) -> GamePhrase:
    query_params = event.get("queryStringParameters")
    if not query_params:
        return None
    phrase = query_params.get("phrase")
    return {
        "ready": GamePhrase.READY,
        "challenge": GamePhrase.CHALLENGE,
        "check": GamePhrase.CHECK,
    }.get(phrase)


def lambda_handler(event, context):  # pylint: disable=W0613

    game_phrase = get_game_phrase(event)
    if not game_phrase:
        return error_response("Phrase parameter is missing or not supported.")

    email, game = get_email_and_game_from_event(event)
    if not email or not game:
        return error_response("Email and Game parameter is missing")
    if not game.isalnum():
        return error_response("Game parameter must be a single alphanumeric word")

    user_data = get_user_data(email)
    if not user_data:
        return error_response("Email not found in the database")

    client_certificate, client_key, endpoint = extract_k8s_credentials(user_data)

    if not all([client_certificate, client_key, endpoint]):
        return error_response("K8s confdential is missing.")

    clear_tmp_directory()
    write_user_files(client_certificate, client_key)

    finished_tasks = get_tasks_by_email_and_game(email, game)
    current_task = get_current_task(game, finished_tasks)
    logger.info(current_task)
    if not current_task:
        return ok_response("All tasks are completed!")

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
        test_result = run_tests(game_phrase, game, current_task)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upload_test_result(
            "/tmp/report.html", game_phrase, now_str, email, game, current_task
        )
        report_url = generate_presigned_url(
            game_phrase, now_str, email, game, current_task
        )

        if test_result == TestResult.OK and game_phrase == GamePhrase.CHECK:
            save_game_task(email, game, current_task)
            run_tests(GamePhrase.CLEANUP, game, current_task)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            upload_test_result(
                "/tmp/report.html",
                GamePhrase.CLEANUP,
                now_str,
                email,
                game,
                current_task,
            )
            return test_result_response(
                game_phrase, test_result, f"{current_task} Completed!", report_url
            )
    except (KeyError, ValueError, RuntimeError) as e:
        return error_response(f"{type(e).__name__}: {str(e)}")

    return test_result_response(
        game_phrase,
        test_result,
        f"{game_phrase.value} is {test_result.name}",
        report_url,
    )
