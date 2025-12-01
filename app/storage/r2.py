import boto3
from botocore.client import Config
from app.config import settings
import boto3
import os
import uuid
import time
from botocore.exceptions import ClientError
from app.utils.logger import logger

def get_r2_client():
    try:
        return boto3.client(
            's3',
            endpoint_url=f"https://{os.getenv('CLOUDFLARE_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_KEY'),
            region_name="auto",
        )
    except Exception as e:
        logger.error(f"Failed to initialize R2 client: {e}")
        raise e

def normalize_key(key: str) -> str:
    # Ensure key is safe and unique if needed, or just return as is if caller handles it.
    # Here we just strip leading slashes.
    return key.lstrip("/")

def upload_stream_to_r2(key: str, file_stream, content_type: str = None, retries=3):
    s3 = get_r2_client()
    bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET')
    
    # Simple mime type guess if not provided
    if not content_type:
        if key.endswith(".png"): content_type = "image/png"
        elif key.endswith(".jpg"): content_type = "image/jpeg"
        elif key.endswith(".mp4"): content_type = "video/mp4"
        elif key.endswith(".wav"): content_type = "audio/wav"
        else: content_type = "application/octet-stream"

    attempt = 0
    while attempt < retries:
        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_stream,
                ContentType=content_type
            )
            
            # Construct public URL (assuming a custom domain or public bucket URL)
            # If using R2.dev subdomain: https://pub-<hash>.r2.dev/<key>
            # For now, we'll use a placeholder or env var for the public domain
            public_domain = os.getenv('R2_PUBLIC_DOMAIN', 'https://cdn.omniai.app')
            url = f"{public_domain}/{key}"
            
            logger.info(f"Successfully uploaded {key} to R2")
            return {"key": key, "url": url}
            
        except ClientError as e:
            attempt += 1
            logger.warning(f"R2 Upload attempt {attempt} failed: {e}")
            if attempt >= retries:
                logger.error(f"Failed to upload {key} after {retries} attempts.")
                raise e
            time.sleep(1 * attempt) # Exponential backoff-ish

def generate_signed_url(key: str, expiration=3600):
    s3 = get_r2_client()
    bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET')
    try:
        response = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': key},
                                            ExpiresIn=expiration)
        return response
    except ClientError as e:
        logger.error(f"Failed to generate signed URL for {key}: {e}")
        return None

def upload_public(filename: str, data: bytes, content_type: str = None):
    """
    Helper for uploading bytes directly with a generated unique key prefix.
    """
    unique_key = f"{uuid.uuid4()}/{filename}"
    return upload_stream_to_r2(unique_key, data, content_type)
