import json
import os
import boto3
import base64
import cgi
from io import BytesIO

dynamodb = boto3.resource('dynamodb')
account_table_name = os.environ['AccountTable'] if 'AccountTable' in os.environ else 'AccountTable'
account_table = dynamodb.Table(account_table_name)


def lambda_handler(event, context):

    # Check if the HTTP method is GET
    if event['httpMethod'] == 'GET':
        # Read the content of 'save-account.html'
        with open('save-account.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    if event['httpMethod'] == 'POST':
        content_type = event['headers'].get(
            'Content-Type') or event['headers'].get('content-type')
        if content_type.startswith('multipart/form-data'):
            post_data = base64.b64decode(event['body']) if event.get(
                'isBase64Encoded') else event['body'].encode('utf-8')
            environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            fs = cgi.FieldStorage(fp=BytesIO(post_data),
                                  environ=environ, headers=event['headers'])

            email = fs.getvalue('email')
            endpoint = fs.getvalue('endpoint')
            client_certificate = fs['client-certificate'].file.read()
            client_key = fs['client-key'].file.read()

            account_table.put_item(Item={
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
