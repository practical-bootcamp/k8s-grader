import json
import os


def setup_paths():
    os.environ["PATH"] += os.pathsep + "/opt/kubectl/"
    os.environ["PATH"] += os.pathsep + "/opt/helm/"


def error_response(message):
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "Error", "message": message}),
    }
