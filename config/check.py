import os
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def masked(v):
    if v is None: return None
    return f"{len(v)} chars: {v[:4]}...{v[-4:]}"

print("ACCOUNT :", masked(os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")))
print("ACCESS  :", masked(os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID") or os.getenv('R2_ACCESS_KEY') or os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')))
print("SECRET  :", masked(os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY") or os.getenv('R2_SECRET_ACCESS_KEY')))
print("BUCKET  :", masked(os.getenv("CLOUDFLARE_R2_BUCKET_NAME")))