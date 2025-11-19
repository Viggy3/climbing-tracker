# test_r2.py
import os, sys
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def masked(v):
    if not v: return None
    if len(v) <= 8: return v
    return v[:4] + "..." + v[-4:]

# try to load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except Exception:
    pass

# check multiple common env-names (try to be forgiving)
candidates = {
    "account": (os.getenv("CLOUDFLARE_ACCOUNT_ID") or os.getenv("CLOUDFLARE_R2_ACCOUNT_ID") or os.getenv("ACCOUNT_ID")),
    "access":  (os.getenv("R2_ACCESS_KEY_ID") or os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID") or os.getenv("R2_ACCESS_KEY") or os.getenv("AWS_ACCESS_KEY_ID")),
    "secret":  (os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY") or os.getenv("R2_SECRET") or os.getenv("AWS_SECRET_ACCESS_KEY")),
    "bucket":  (os.getenv("R2_BUCKET") or os.getenv("CLOUDFLARE_R2_BUCKET_NAME") or os.getenv("BUCKET")),
}

print("Detected environment variables (masked):")
for k,v in candidates.items():
    print(f"  {k:6}: {masked(v)}")

if not candidates["account"] or not candidates["access"] or not candidates["secret"]:
    print("\nERROR: Missing one or more required env vars (account/access/secret).")
    print("Make sure you set them in the same terminal session before running python.")
    sys.exit(2)

if not all([candidates.get("account"), candidates.get("access"), candidates.get("secret"), candidates.get("bucket")]):
    print("\nERROR: missing one or more R2_* environment variables")
    raise SystemExit(1)

endpoint = f"https://{candidates['account']}.r2.cloudflarestorage.com"
s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=candidates["access"],
    aws_secret_access_key=candidates["secret"],
    region_name="auto",
)

print(f"\nListing objects in bucket: {candidates['bucket']!r}")
try:
    resp = s3.list_objects_v2(Bucket=candidates["bucket"])
    contents = resp.get("Contents", [])
    if not contents:
        print("  (bucket is reachable, but empty)")
    else:
        for obj in contents:
            print("  -", obj["Key"])
    print("\n✅ R2 connection OK")
except ClientError as e:
    print("\n❌ ClientError while listing objects:")
    print(e)