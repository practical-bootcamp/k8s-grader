import logging
import os
import re

import boto3
from common.database import get_api_key, save_api_key
from common.handler import text_response
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SECRET_HASH = os.getenv("SecretHash")
API_GATEWAY_API_NAME = os.getenv("ApiGateWayName")
USAGE_PLAN_ID_NAME = os.getenv("UsagePlanName")
STAGE_NAME = os.getenv("StageName")

client = boto3.client("apigateway")


def lambda_handler(event, context):  # pylint: disable=W0613

    query_params = event.get("queryStringParameters")
    secret = None
    email = None
    if query_params:
        secret = query_params.get("secret")
        email = query_params.get("email")
    if not secret or not email:
        return text_response("Secret and email parameter is missing.")
    if secret != SECRET_HASH:
        return text_response("Invalid secret")
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return text_response("Invalid email address.")

    api_key = get_api_key(email)
    if api_key:
        return text_response(api_key)

    rest_apis = client.get_rest_apis().get("items")
    rest_api_id = None
    for api in rest_apis:
        if api.get("name") == API_GATEWAY_API_NAME:
            rest_api_id = api.get("id")
            break
    if not rest_api_id:
        return text_response("API Gateway API not found.")

    fernet = Fernet(secret)
    token = fernet.encrypt(email.encode()).decode()

    api_key_response = client.create_api_key(
        name=email,
        value=token,
        enabled=True,
        stageKeys=[
            {"restApiId": rest_api_id, "stageName": STAGE_NAME},
        ],
    )
    api_key = api_key_response.get("id")
    if not api_key:
        return text_response("Failed to create API key.")

    usage_plans = client.get_usage_plans().get("items")
    usage_plan_id = None
    for plan in usage_plans:
        if plan.get("name") == USAGE_PLAN_ID_NAME:
            usage_plan_id = plan.get("id")
            break
    if not usage_plan_id:
        return text_response("Usage plan not found.")

    client.create_usage_plan_key(
        usagePlanId=usage_plan_id, keyId=api_key, keyType="API_KEY"
    )
    api_key_details = client.get_api_key(apiKey=api_key, includeValue=True)
    api_key_value = api_key_details.get("value")
    if not api_key_value:
        return text_response("Failed to retrieve API key value.")

    save_api_key(email, api_key_value)

    return text_response(api_key_value)
