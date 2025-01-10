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

    # Upload the file
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
    game_phase: GamePhrase, time, email, game, task, expiration=3600
):
    object_name_with_time = (
        f"{game}/{email}/{task}/test_report_{game_phase.name}_{time}.html"
    )
    # Generate a presigned URL for the S3 object
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

    # The response contains the presigned URL
    return response
