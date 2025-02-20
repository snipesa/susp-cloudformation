import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    alarm_name = event['detail']['alarmName']  
    current_state = event['detail']['state']['value']  # "OK" or "ALARM"
    previous_state = event['detail']['previousState']['value']  # "OK" or "ALARM"
    
    print(f"Health check {alarm_name} changed from {previous_state} to {current_state}")

    S3_BUCKET = 'website-status-bucket'

    try:
        try:
            existing_status = json.loads(
                s3.get_object(Bucket=S3_BUCKET, Key='status.json')['Body'].read()
            )
        except s3.exceptions.NoSuchKey:
            existing_status = {}
            
        # Update status information
        existing_status[alarm_name] = {
            'status': 'Operational' if current_state == "OK" else 'Down',
            'lastChecked': datetime.now().isoformat()        
            }
        Body = json.dumps(existing_status, separators=(',', ': '))
        print(Body)
        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key='status.json',
            Body=json.dumps(existing_status, indent=2),
            ContentType='application/json',
            CacheControl='no-cache'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(existing_status)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }