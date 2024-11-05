import json
import os
import boto3
import base64
import cgi
from io import BytesIO

K8sAccountTable = os.environ['K8sAccountTable']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(K8sAccountTable)

def lambda_handler(event, context):   

    # Check if the HTTP method is GET
    if event['httpMethod'] == 'GET':
        # Read the content of 'save-account.html'
        with open('save-account.html', 'r') as f:
            html_content = f.read()
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    if event['httpMethod'] == 'POST':
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if content_type.startswith('multipart/form-data'):
            post_data = base64.b64decode(event['body']) if event.get('isBase64Encoded') else event['body'].encode('utf-8')
            environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            fs = cgi.FieldStorage(fp=BytesIO(post_data), environ=environ, headers=event['headers'])

            email = fs.getvalue('email')
            endpoint = fs.getvalue('endpoint')
            client_certificate = fs['client-certificate'].file.read()
            client_key = fs['client-key'].file.read()

            table.put_item(Item={
                'email': email,
                'endpoint': endpoint,
                'client_certificate': client_certificate.decode('utf-8'),
                'client_key': client_key.decode('utf-8')
            })

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Data saved successfully'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Unsupported content type'})
            }
