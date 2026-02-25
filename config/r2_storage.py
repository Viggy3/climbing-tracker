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
        worker_url = f"tracker-media-proxy.hariviggy333.workers.dev/media/{unique_filename}"
        print(f"Upload successful to R2, serving via worker: {worker_url}")
        return worker_url
        
    except (NoCredentialsError, ClientError) as e:
        print(f"❌ R2 Upload Failed - Credentials Error: {e}")
        return None
    except Exception as e:
        print(f"❌ R2 Upload Failed - Unexpected Error: {e}")
        return None



def delete_from_r2(media_key):
    try: 
        r2  = get_r2()
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")

        if media_key is None:
            print("❌ R2 Deletion Failed - media_key is None")
            return False
        if media_key.startswith("tracker-media-proxy.hariviggy333.workers.dev/media/"):
            r2_key = media_key.split("/media/")[1]
        else:
            r2_key = media_key
        print(f"Deleting from R2 - Bucket: {bucket_name}, Key: {r2_key}")
        r2.delete_object(Bucket=bucket_name, Key=r2_key)
        print("✅ R2 Deletion Successful")
        return True
    except (NoCredentialsError, ClientError) as e:
        print(f"❌ R2 Deletion Failed - Credentials Error: {e}")
        return False
    except Exception as e:
        print(f"❌ R2 Deletion Failed - Unexpected Error: {e}")
        return False

import subprocess
import tempfile
import imageio_ffmpeg

def generate_thumbnail(video_key, user_id, tracker_id):
    try:
        r2 = get_r2()
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        # Download video to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
            r2.download_fileobj(bucket_name, video_key, tmp_video)
            tmp_video_path = tmp_video.name

        # Extract frame at 1 second to temp jpg
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_thumb:
            tmp_thumb_path = tmp_thumb.name

        subprocess.run([
            ffmpeg_path,
            '-i', tmp_video_path,
            '-ss', '00:00:01',
            '-vframes', '1',
            '-y',
            tmp_thumb_path
        ], check=True, capture_output=True)

        # Upload thumbnail to R2
        thumb_key = f"{user_id}/{tracker_id}/{uuid.uuid4()}_thumb.jpg"
        with open(tmp_thumb_path, 'rb') as f:
            r2.upload_fileobj(
                Fileobj=f,
                Bucket=bucket_name,
                Key=thumb_key,
                ExtraArgs={"ContentType": "image/jpeg"}
            )

        # Cleanup temp files
        os.unlink(tmp_video_path)
        os.unlink(tmp_thumb_path)

        worker_url = f"tracker-media-proxy.hariviggy333.workers.dev/media/{thumb_key}"
        print(f"✅ Thumbnail generated: {worker_url}")
        return worker_url

    except Exception as e:
        print(f"❌ Thumbnail generation failed: {e}")
        return None