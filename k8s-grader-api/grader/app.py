import json
import os
import base64
import boto3
from kubernetes import client, config

dynamodb = boto3.resource('dynamodb')
table_name =  os.environ['K8sAccountTable']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    email = event.get('queryStringParameters', {}).get('email')
    if not email:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Email parameter is missing"})
        }

    try:
        response = table.get_item(Key={'email': email})
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error accessing DynamoDB"})
        }

    if 'Item' not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Email not found in the database"})
        }

    user_data = response['Item']
    client_certificate = user_data.get('client_certificate')
    client_key = user_data.get('client_key')
    endpoint = user_data.get('endpoint')

    if not all([client_certificate, client_key, endpoint]):
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Incomplete user data"})
        }

    kube_config = build_kube_config(client_certificate, client_key, endpoint)

    try:     
        config.load_kube_config_from_dict(kube_config)
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        node_info = [
            {"name": item.metadata.name, "ip": item.status.addresses[0].address} for item in nodes.items
        ]
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error accessing Kubernetes API"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"nodes": node_info})
    }

def build_kube_config(client_certificate, client_key, endpoint):
    cert_data = base64.b64encode(client_certificate.encode('utf-8')).decode('utf-8')
    key_data = base64.b64encode(client_key.encode('utf-8')).decode('utf-8')

    return {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [
            {
                "name": "k8s-cluster",
                "cluster": {
                    "server": endpoint
                }
            }
        ],
        "contexts": [
            {
                "name": "k8s-context",
                "context": {
                    "cluster": "k8s-cluster",
                    "user": "k8s-user"
                }
            }
        ],
        "current-context": "k8s-context",
        "users": [
            {
                "name": "k8s-user",
                "user": {
                    "client-certificate-data": cert_data,
                    "client-key-data": key_data
                }
            }
        ]
    }