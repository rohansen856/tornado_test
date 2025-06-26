import boto3
import os
from botocore.exceptions import ClientError

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-tornado-bucket')

def ensure_bucket_exists():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            raise
