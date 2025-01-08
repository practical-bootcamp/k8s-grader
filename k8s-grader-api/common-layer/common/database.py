import os
import boto3

dynamodb = boto3.resource('dynamodb')

account_table = dynamodb.Table(os.getenv('AccountTable'))
game_task_table = dynamodb.Table(os.getenv('GameTaskTable'))
score_table = dynamodb.Table(os.getenv('ScoreTable'))
session_table = dynamodb.Table(os.getenv('SessionTable'))


def get_email_from_event(event):
    return event.get('queryStringParameters', {}).get('email')


def get_user_data(email):
    try:
        response = account_table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception:
        return None


def get_game_tasks_by_email_and_game(email, game):

    response = game_task_table.query(
        KeyConditionExpression='email = :email and begins_with(game, :game)',
        ExpressionAttributeValues={
            ':email': email,
            ':game': f'{game}#'
        },
        # This will sort the results by the game attribute in ascending order
        ScanIndexForward=True
    )
    return response.get('Items')
