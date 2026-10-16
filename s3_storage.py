import boto3
import os
import io
from typing import Optional
from botocore.client import Config
from botocore.exceptions import ClientError


class S3Storage:
    def __init__(self):
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'dataloom-bucket')
        self.endpoint_url = os.environ.get('S3_ENDPOINT_URL', 'https://s3.dbrij.com')
        
        access_key = os.environ.get('DBRIJ_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('DBRIJ_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if not access_key or not secret_key:
            raise ValueError("Storage credentials not configured")
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        
        # Verify bucket exists
    
    def _verify_bucket(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise ValueError(f"Bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                raise ValueError(f"Access denied to bucket '{self.bucket_name}'. Check credentials.")
            else:
                raise ValueError(f"Error accessing bucket: {e}")
    
    def upload_file(self, file_data: bytes, file_key: str, content_type: str = 'application/octet-stream') -> bool:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False
    
    def download_file(self, file_key: str) -> Optional[bytes]:
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    def file_exists(self, file_key: str) -> bool:
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False
    
    def generate_file_key(self, user_id: int, file_id: int, filename: str) -> str:
        safe_filename = filename.replace('../', '').replace('..\\', '')
        return f"users/{user_id}/files/{file_id}/{safe_filename}"
    
    def get_file_url(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
