import json
import os
import shutil
import pytest

from common.helper import get_email_from_event, get_user_data, clear_tmp_directory, write_user_files, create_json_input

os.environ["PATH"] += os.pathsep + "/opt/kubectl/"
os.environ["PATH"] += os.pathsep + "/opt/helm/"


def run_tests():
    shutil.copy('k8s-tests.zip', '/tmp/k8s-tests.zip')
    shutil.unpack_archive('/tmp/k8s-tests.zip', '/tmp/')
    return pytest.main(["-x", "/tmp/k8s-tests"])


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

    client_certificate = user_data.get('client_certificate')
    client_key = user_data.get('client_key')
    endpoint = user_data.get('endpoint')

    if not all([client_certificate, client_key, endpoint]):
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Incomplete user data"})
        }

    try:
        clear_tmp_directory()
        write_user_files(client_certificate, client_key)
        create_json_input(endpoint, {"namespace": "demo"})
        retcode = run_tests()
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"retcode": retcode})
    }
