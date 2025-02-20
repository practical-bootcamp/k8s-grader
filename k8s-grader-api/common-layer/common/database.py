import json
import os
import time
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key
from common.pytest import GamePhrase, TestResult

dynamodb = boto3.resource("dynamodb")

account_table = dynamodb.Table(os.getenv("AccountTable"))
game_task_table = dynamodb.Table(os.getenv("GameTaskTable"))
session_table = dynamodb.Table(os.getenv("SessionTable"))
api_key_table = dynamodb.Table(os.getenv("ApiKeyTable"))
test_record_table = dynamodb.Table(os.getenv("TestRecordTable"))
npc_task_table = dynamodb.Table(os.getenv("NpcTaskTable"))
npc_lock_table = dynamodb.Table(os.getenv("NpcLockTable"))
npc_background_table = dynamodb.Table(os.getenv("NpcBackgroundTable"))


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


def delete_game_task(email, game, task):
    game_task_table.delete_item(Key={"email": email, "game": f"{game}#{task}"})


def save_game_session(email, game, task, session):
    session_table.put_item(
        Item={
            "email": email,
            "game": f"{game}#{task}",
            "session": json.dumps(session),
            "time": int(time.time()),
        }
    )


def delete_game_session(email, game, task):
    session_table.delete_item(Key={"email": email, "game": f"{game}#{task}"})


def get_game_session(email, game, task):
    response = session_table.get_item(Key={"email": email, "game": f"{game}#{task}"})
    item = response.get("Item")
    if item:
        return json.loads(item["session"])
    return None


def get_api_key(email):
    response = api_key_table.get_item(Key={"email": email})
    item = response.get("Item")
    if item:
        return item["api_key"]
    return None


def save_api_key(email, api_key):
    api_key_table.put_item(Item={"email": email, "api_key": api_key})


def save_test_record(
    email: str,
    game: str,
    current_task,
    game_phase: GamePhrase,
    test_result: TestResult,
    bucket: str,
    key: str,
    report_url: str,
    now_str: str,
):
    test_record_table.put_item(
        Item={
            "email": email,
            "gameTime": game + "#" + now_str,
            "task": current_task,
            "gamePhase": game_phase.name,
            "bucket": bucket,
            "key": key,
            "reportUrl": report_url,
            "time": now_str,
        }
    )


def save_npc_task(email, game, task):
    npc_task_table.put_item(
        Item={"email": email, "game": f"{game}#{task}", "time": int(time.time())}
    )


def save_npc_lock(email, game, npc):
    expiration_time = int((datetime.now() + timedelta(minutes=30)).timestamp())
    npc_lock_table.put_item(
        Item={
            "email": email,
            "gameNpc": game + "#" + npc,
            "ttl": expiration_time,
            "time": int(time.time()),
        }
    )


def get_npc_lock(email, game, npc):
    response = npc_lock_table.get_item(
        Key={"email": email, "gameNpc": game + "#" + npc}
    )
    item = response.get("Item")
    if item:
        return item
    return None


def get_npc_background(name):
    response = npc_background_table.get_item(Key={"name": name})
    item = response.get("Item")
    if item:
        return {
            "name": item.get("name"),
            "age": item.get("age"),
            "gender": item.get("gender"),
            "background": item.get("background"),
        }
    return None


def save_npc_background(name, age, gender, background):
    npc_background_table.put_item(
        Item={
            "name": name,
            "age": age,
            "gender": gender,
            "background": background,
            "time": int(time.time()),
        }
    )
