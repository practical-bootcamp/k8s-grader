import os

import boto3
from botocore.exceptions import NoCredentialsError
from common.pytest import GamePhrase

TestResultBucket = os.getenv("TestResultBucket")


def upload_test_result(file_name, game_phase: GamePhrase, time, email, game, task):
    object_name = f"{game}/{email}/{task}/a_test_report_{game_phase.name}.html"
    object_name_with_time = (
        f"{game}/{email}/{task}/test_report_{game_phase.name}_{time}.html"
    )

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            file_name,
            TestResultBucket,
            object_name,
            ExtraArgs={"ContentType": "text/html"},
        )
        s3_client.upload_file(
            file_name,
            TestResultBucket,
            object_name_with_time,
            ExtraArgs={"ContentType": "text/html"},
        )
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True


def generate_presigned_url(
    game_phase: GamePhrase,
    time,
    email,
    game,
    task,
    expiration=604800,  # 7 days in seconds
):
    _, object_name_with_time = get_bucket_key(email, game, task, game_phase, time)

    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": TestResultBucket, "Key": object_name_with_time},
            ExpiresIn=expiration,
        )
    except NoCredentialsError:
        print("Credentials not available")
        return None

    return response


def get_bucket_key(email, game, task, game_phase: GamePhrase, time):
    object_name_with_time = (
        f"{game}/{email}/{task}/test_report_{game_phase.name}_{time}.html"
    )
    return TestResultBucket, object_name_with_time
