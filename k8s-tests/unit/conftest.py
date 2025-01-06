import json
import os
import pytest


@pytest.fixture(scope='session', autouse=True)
def json_input():
    if not os.path.exists("/tmp/json_input.json"):
        with open('/workspaces/k8s-grader/k8s/minikube/endpoint.txt', 'r', encoding='utf-8') as endpoint_file:
            host = endpoint_file.read().strip()
        result = {
            "cert_file": '/workspaces/k8s-grader/k8s/minikube/downloaded_files/client.crt',
            "key_file": '/workspaces/k8s-grader/k8s/minikube/downloaded_files/client.key',
            "host": host
        }       
        return result
    with open("/tmp/json_input.json", 'r', encoding="utf-8") as file:
        json_str_input = file.read()
        result = json.loads(json_str_input)
    return result