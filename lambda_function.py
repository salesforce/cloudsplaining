import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Cloudsplaining Lambda is working!')
    }

