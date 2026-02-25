import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_r2():
    account_id = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
    access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
    secret_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    
    print(f"Using account ID: {account_id[:8]}...")
    print(f"Using access key: {access_key[:8]}...")
    
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=boto3.session.Config(
            s3={
                'addressing_style': 'path'
            },
            signature_version='s3v4'
        )
    )

def upload_to_storage(file, tracker_id, user_id, unique_filename=None):
    try:
        r2 = get_r2()
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        
        print(f"Uploading to bucket: {bucket_name}")
        
        if not bucket_name:
            raise ValueError("CLOUDFLARE_R2_BUCKET_NAME environment variable is not set")

        # Use provided filename or create a unique one
        if unique_filename is None:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{user_id}/{tracker_id}/{uuid.uuid4()}{file_extension}"
        
        print(f"Upload path: {unique_filename}")

        # Reset file pointer to beginning
        file.file.seek(0)
        
        # Upload with explicit content type directly to R2
        r2.upload_fileobj(
            Fileobj=file.file,
            Bucket=bucket_name,
            Key=unique_filename,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream"
            }
        )
        
        # Upload successful to R2, but return worker URL for serving
        return unique_filename 
        
    except (NoCredentialsError, ClientError) as e:
        print(f"❌ R2 Upload Failed - Credentials Error: {e}")
        return None
    except Exception as e:
        print(f"❌ R2 Upload Failed - Unexpected Error: {e}")
        return None



def delete_from_r2(media_key):
    try:
        r2 = get_r2()
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        if media_key is None:
            print("❌ R2 Deletion Failed - media_key is None")
            return False
        print(f"Deleting from R2 - Bucket: {bucket_name}, Key: {media_key}")
        r2.delete_object(Bucket=bucket_name, Key=media_key)
        print("✅ R2 Deletion Successful")
        return True
    except (NoCredentialsError, ClientError) as e:
        print(f"❌ R2 Deletion Failed: {e}")
        return False

