import json
import os
import boto3
import shutil

import pytest

os.environ["PATH"] += os.pathsep + "/opt/kubectl/"

dynamodb = boto3.resource('dynamodb')
account_table_name = os.environ['AccountTable'] \
    if 'AccountTable' in os.environ else 'AccountTable'
account_table = dynamodb.Table(account_table_name)


def lambda_handler(event, context):
    email = event.get('queryStringParameters', {}).get('email')
    if not email:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Email parameter is missing"})
        }

    try:
        response = account_table.get_item(Key={'email': email})
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error accessing DynamoDB"})
        }

    if 'Item' not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Email not found in the database"})
        }

    user_data = response['Item']
    client_certificate = user_data.get('client_certificate')
    client_key = user_data.get('client_key')
    endpoint = user_data.get('endpoint')

    if not all([client_certificate, client_key, endpoint]):
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Incomplete user data"})
        }
    
    for filename in os.listdir('/tmp/'):
        file_path = os.path.join('/tmp/', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": f"Failed to delete {file_path}. Reason: {e}"})
            }

    with open('/tmp/client_certificate.crt', 'w', encoding='utf-8') as cert_file:
        cert_file.write(client_certificate)
    with open('/tmp/client_key.key', 'w', encoding='utf-8') as key_file:
        key_file.write(client_key)

    json_input = {
        "cert_file": '/tmp/client_certificate.crt',
        "key_file": '/tmp/client_key.key',
        "host": endpoint
    }
    with open('/tmp/json_input.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_input, json_file)

    try:

        shutil.copy('k8s-tests.zip', '/tmp/k8s-tests.zip')
        shutil.unpack_archive('/tmp/k8s-tests.zip', '/tmp/')

        files = os.listdir('/tmp/k8s-tests/unit/game01/')
        print(files)

        retcode = pytest.main(["-x", "/tmp/k8s-tests"])
        print(retcode)

    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error running kubectl command"})
        }

    return {
        "statusCode": 200,
        "body": retcode
    }
