import json
import os
import time

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")

account_table = dynamodb.Table(os.getenv("AccountTable"))
game_task_table = dynamodb.Table(os.getenv("GameTaskTable"))
score_table = dynamodb.Table(os.getenv("ScoreTable"))
session_table = dynamodb.Table(os.getenv("SessionTable"))


def is_endpoint_exist(email, endpoint):
    response = account_table.query(
        IndexName="EndpointIndex", KeyConditionExpression=Key("endpoint").eq(endpoint)
    )
    items = response.get("Items", [])
    if items:
        return items[0].get("email") != email
    return False


def save_account(email, endpoint, client_certificate, client_key):
    account_table.put_item(
        Item={
            "email": email,
            "endpoint": endpoint,
            "client_certificate": client_certificate,
            "client_key": client_key,
            "time": int(time.time()),
        }
    )


def get_email_from_event(event):
    query_params = event.get("queryStringParameters")
    if query_params:
        return query_params.get("email")
    return None


def get_user_data(email):
    response = account_table.get_item(Key={"email": email})
    return response.get("Item")


def get_tasks_by_email_and_game(email, game):

    response = game_task_table.query(
        KeyConditionExpression=Key("email").eq(email)
        & Key("game").begins_with(f"{game}#")
    )

    items = response.get("Items", [])
    return sorted([item["game"].split("#", 1)[1] for item in items])


def save_game_task(email, game, task):
    game_task_table.put_item(
        Item={"email": email, "game": f"{game}#{task}", "time": int(time.time())}
    )


def save_game_session(email, game, task, session):
    session_table.put_item(
        Item={
            "email": email,
            "game": f"{game}#{task}",
            "session": json.dumps(session),
            "time": int(time.time()),
        }
    )


def get_game_session(email, game, task):
    response = session_table.get_item(Key={"email": email, "game": f"{game}#{task}"})
    item = response.get("Item")
    if item:
        return json.loads(item["session"])
    return None
