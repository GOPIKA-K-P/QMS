import boto3

nosql_connection = boto3.resource('dynamodb', endpoint_url='http://172.29.168.41:8000')
