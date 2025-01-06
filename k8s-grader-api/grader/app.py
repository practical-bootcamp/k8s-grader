import json
import os
import boto3
import shutil
import pytest

os.environ["PATH"] += os.pathsep + "/opt/kubectl/"

dynamodb = boto3.resource('dynamodb')
account_table_name = os.getenv('AccountTable', 'AccountTable')
account_table = dynamodb.Table(account_table_name)


def get_email_from_event(event):
    return event.get('queryStringParameters', {}).get('email')


def get_user_data(email):
    try:
        response = account_table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception:
        return None


def clear_tmp_directory():
    for filename in os.listdir('/tmp/'):
        file_path = os.path.join('/tmp/', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            raise Exception(f"Failed to delete {file_path}. Reason: {e}")


def write_user_files(client_certificate, client_key):
    with open('/tmp/client_certificate.crt', 'w', encoding='utf-8') as cert_file:
        cert_file.write(client_certificate)
    with open('/tmp/client_key.key', 'w', encoding='utf-8') as key_file:
        key_file.write(client_key)


def create_json_input(endpoint, extra_data={}):
    json_input = {
        "cert_file": '/tmp/client_certificate.crt',
        "key_file": '/tmp/client_key.key',
        "host": endpoint
    }
    json_input.update(extra_data)
    with open('/tmp/json_input.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_input, json_file)


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
