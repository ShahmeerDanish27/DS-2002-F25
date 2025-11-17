#!/bin/bash

# Lab 8 – Part 2 Script
# Usage example:
#    ./upload_and_presign.sh myimage.png ds2002-f25-ymf5zb 604800

# Positional arguments
LOCAL_FILE=$1
BUCKET=$2
EXPIRATION=$3

# Check arguments
if [ $# -ne 3 ]; then
  echo "Usage: $0 <local_file> <bucket_name> <expiration_seconds>"
  exit 1
fi

echo "Uploading $LOCAL_FILE to s3://$BUCKET/ ..."
aws s3 cp "$LOCAL_FILE" "s3://$BUCKET/"

echo "Generating presigned URL for $LOCAL_FILE ..."
URL=$(aws s3 presign "s3://$BUCKET/$LOCAL_FILE" --expires-in $EXPIRATION)

echo
echo "============================"
echo "Presigned URL:"
echo "$URL"
echo "============================"
echo
echo "Expiration (seconds): $EXPIRATION"
echo "Done!"
