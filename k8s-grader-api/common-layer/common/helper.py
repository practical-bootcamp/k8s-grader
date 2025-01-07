import json
import os
import boto3
import shutil

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
            raise RuntimeError(f"Failed to delete {file_path}. Reason: {e}") from e


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
