import json
import os
import boto3

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


def get_user_data_from_event(event):
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

    return user_data
