#!/usr/bin/env python3

import sys
import os
from urllib.parse import urlparse

import requests
import boto3


def download_file(url: str, local_filename: str | None = None) -> str:
    """
    Download a file from the given URL and save it locally.
    Returns the local filename.
    """
    if local_filename is None:
        # Try to get a name from the URL path
        path = urlparse(url).path
        basename = os.path.basename(path)
        if basename == "":
            basename = "downloaded_file"
        local_filename = basename

    print(f"Downloading {url} ...")

    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    with open(local_filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Saved to {local_filename}")
    return local_filename


def upload_to_s3(local_file: str, bucket_name: str, object_name: str) -> None:
    """
    Upload a local file to S3 using boto3.
    """
    print(f"Uploading {local_file} to s3://{bucket_name}/{object_name} ...")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.upload_file(local_file, bucket_name, object_name)
    print("Upload complete.")


def generate_presigned_url(bucket_name: str, object_name: str, expires_in: int) -> str:
    """
    Generate a presigned URL for the given S3 object.
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=expires_in,
    )
    return response


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 s3_presign_boto3.py <file_url> <bucket_name> <expires_in_seconds>"
        )
        sys.exit(1)

    file_url = sys.argv[1]
    bucket_name = sys.argv[2]
    expires_in = int(sys.argv[3])

    # 1. Download file from the internet
    local_file = download_file(file_url)

    # Use the same name in S3 as local filename
    object_name = os.path.basename(local_file)

    # 2. Upload to S3
    upload_to_s3(local_file, bucket_name, object_name)

    # 3. Generate presigned URL
    print("Generating presigned URL ...")
    url = generate_presigned_url(bucket_name, object_name, expires_in)

    print("\nPresigned URL:")
    print(url)
    print(f"\nThis URL will work for {expires_in} seconds.")


if __name__ == "__main__":
    main()

