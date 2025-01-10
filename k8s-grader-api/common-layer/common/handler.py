import json
import os

from common.pytest import GamePhrase, TestResult


def setup_paths():
    os.environ["PATH"] += os.pathsep + "/opt/kubectl/"
    os.environ["PATH"] += os.pathsep + "/opt/helm/"


def error_response(message):
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "Error", "message": message}),
    }


def ok_response(message):
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "OK", "message": message}),
    }


def html_response(html_content):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html_content,
    }


def test_result_response(
    game_phrase: GamePhrase, test_result: TestResult, instruction, report_url
):
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "game_phrase": game_phrase.name,
                "status": test_result.name,
                "message": instruction,
                "report_url": report_url,
            }
        ),
    }


def extract_k8s_credentials(user_data):
    client_certificate = user_data.get("client_certificate")
    client_key = user_data.get("client_key")
    endpoint = user_data.get("endpoint")
    return client_certificate, client_key, endpoint


def get_email_and_game_from_event(event):
    query_params = event.get("queryStringParameters")
    if query_params:
        return query_params.get("email"), query_params.get("game")
    return None, None
