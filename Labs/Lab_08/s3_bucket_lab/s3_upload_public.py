import sys
import boto3

if len(sys.argv) != 4:
    print("Usage: python3 s3_upload_public.py <local_file> <bucket_name> <s3_key>")
    sys.exit(1)

local_file = sys.argv[1]
bucket = sys.argv[2]
s3_key = sys.argv[3]

s3 = boto3.client("s3", region_name="us-east-1")

# The ACL makes the file PUBLIC
s3.upload_file(
    Filename=local_file,
    Bucket=bucket,
    Key=s3_key,
    ExtraArgs={'ACL': 'public-read'}
)

print("Upload complete! Your public URL is:")
print(f"https://s3.amazonaws.com/{bucket}/{s3_key}")

