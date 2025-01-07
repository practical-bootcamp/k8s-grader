import json
import os


from common.fs_helper import clear_tmp_directory, write_user_files, create_json_input
from common.db_helper import get_email_from_event, get_user_data
from common.pytest_helper import run_tests, GamePhase

os.environ["PATH"] += os.pathsep + "/opt/kubectl/"
os.environ["PATH"] += os.pathsep + "/opt/helm/"


def lambda_handler(event, context):

    email = get_email_from_event(event)
    if not email:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Email parameter is missing"})
        }

    user_data = get_user_data(email)
    if not user_data:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Email not found in the database"})
        }

    if isinstance(user_data, dict) and "statusCode" in user_data:
        return user_data

    client_certificate = user_data.get('client_certificate')
    client_key = user_data.get('client_key')
    endpoint = user_data.get('endpoint')

    if not all([client_certificate, client_key, endpoint]):
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Incomplete user data"})
        }
    clear_tmp_directory()
    write_user_files(client_certificate, client_key)

    try:
        create_json_input(endpoint, {"namespace": "demo"})
        retcode = run_tests(GamePhase.CHECK, "game01",
                            "test_02_create_namespace.py")
        with open('/tmp/report.html', 'r', encoding="utf-8") as log_file:
            log_content = log_file.read()
        print(log_content)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"retcode": retcode, "log_content": log_content})
    }
