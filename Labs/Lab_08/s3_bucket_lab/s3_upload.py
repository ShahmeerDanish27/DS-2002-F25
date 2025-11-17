import sys
import boto3
from botocore.exceptions import ClientError

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 s3_upload_private.py <local_file_path> <bucket_name> <s3_key>")
        sys.exit(1)

    local_file = sys.argv[1]
    bucket_name = sys.argv[2]
    s3_key = sys.argv[3]

    # Create S3 client (region must match your lab: us-east-1)
    s3 = boto3.client("s3", region_name="us-east-1")

    try:
        print(f"Uploading {local_file} to s3://{bucket_name}/{s3_key} ...")

        # This keeps the file PRIVATE (no ACL parameter added)
        s3.upload_file(
            Filename=local_file,
            Bucket=bucket_name,
            Key=s3_key
        )

        print("Upload complete!")

        # Construct a public URL to test in your browser
        public_url = f"https://s3.amazonaws.com/{bucket_name}/{s3_key}"
        print("\nTry this public URL in your browser (it should give Permission Denied):")
        print(public_url)

    except FileNotFoundError:
        print(f"ERROR: Local file '{local_file}' not found.")
    except ClientError as e:
        print("AWS ClientError occurred:")
        print(e)
    except Exception as e:
        print("Unexpected error occurred:")
        print(e)

if __name__ == "__main__":
    main()

