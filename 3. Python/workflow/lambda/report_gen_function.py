import json
import boto3

def lambda_handler(event, context):
    print("reporting event:", event)
    return {
        'statusCode': 200,
        'body': json.dumps(f'reporting lambda return')
    }