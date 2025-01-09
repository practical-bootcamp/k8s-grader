import base64
import json
import logging

from common.database import is_endpoint_exist, save_account
from requests_toolbelt.multipart import decoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # Check if the HTTP method is GET
    if event["httpMethod"] == "GET":
        # Read the content of 'save-account.html'
        with open("save-account.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html_content,
        }
    if event["httpMethod"] == "POST":
        content_type = event["headers"].get("Content-Type") or event["headers"].get(
            "content-type"
        )
        if content_type.startswith("multipart/form-data"):
            post_data = (
                base64.b64decode(event["body"])
                if event.get("isBase64Encoded")
                else event["body"].encode("utf-8")
            )

            multipart_data = decoder.MultipartDecoder(post_data, content_type)
            fs = {}
            for part in multipart_data.parts:
                content_disposition = part.headers[b"Content-Disposition"].decode(
                    "utf-8"
                )
                name = content_disposition.split("name=")[1].split(";")[0].strip('"')
                fs[name] = part

            email = fs["email"].text
            endpoint = fs["endpoint"].text
            client_certificate = fs["client-certificate"].text
            client_key = fs["client-key"].text

            if not client_certificate or not client_key:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {"message": "Missing client-certificate or client-key"}
                    ),
                }

            # Validate email and endpoint
            if "@" not in email or "." not in email.split("@")[-1]:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Invalid email format"}),
                }

            if not endpoint.startswith("http://") and not endpoint.startswith(
                "https://"
            ):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Invalid endpoint format"}),
                }

            if is_endpoint_exist(email, endpoint):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "No Sharing K8s cluster"}),
                }

            save_account(email, endpoint, client_certificate, client_key)

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Data saved successfully"}),
            }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Unsupported content type"}),
            }
