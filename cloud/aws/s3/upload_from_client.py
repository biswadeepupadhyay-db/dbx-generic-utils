import os
import sys
import json
import boto3

sys.path.append("./cloud/aws/auth")
import logging


def upload_to_s3(s3_client : boto3.Session.client,
                 bucket_name: str,
                 local_path: str,
                 is_directory: bool=False,
                 s3_key: str =''):
    """
    Upload a file or directory to S3.

    :param s3_client: Boto3 S3 client
    :param bucket_name: Name of the S3 bucket
    :param local_path: Local file path or directory path
    :param is_directory: Flag to indicate if it's a directory upload
    :param s3_key: Optional S3 key prefix
    """
    if not is_directory:
        # Single file upload
        file_name = os.path.basename(local_path)
        s3_path = os.path.join(s3_key, file_name).replace('\\', '/')
        try:
            s3_client.upload_file(local_path, bucket_name, s3_path)
            print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_path}")
        except Exception as e:
            print(f"Error uploading {local_path}: {str(e)}")
    else:
        # Directory upload
        dir_name = os.path.basename(os.path.normpath(local_path))
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_path)
                s3_path = os.path.join(s3_key, dir_name, relative_path).replace('\\', '/')
                try:
                    s3_client.upload_file(local_file_path, bucket_name, s3_path)
                    print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_path}")
                except Exception as e:
                    print(f"Error uploading {local_file_path}: {str(e)}")

var_auth_method = input("Select your Auth Method to AWS:\n1. SSO\n2. Access Keys\n[Choose between (1) & (2)] [Default: (1)]:") or "1"

var_local_path = input("Local file or Directory path: ")
var_directory_input = input("Is your local path a directory? [Default: 'no']: ") or "no"
var_directory_flag = False if var_directory_input.lower() == "no" else True
var_bucket_name = input("S3 bucket name: ")
var_s3_key = input("S3 key prefix: [Default: '']: ") or ''


if var_auth_method == "1":
    AWS_DEFAULT_REGION = input("Enter your default AWS Region: [Default: us-east-1]: ") or "us-east-1"
    os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION
    aws_profile_name = input("Enter your AWS Profile Name: You can find that inside `~/.aws/config`: ") or None
    if not aws_profile_name:
        raise ValueError("You must enter your AWS Profile Name.")
    from sso import set_aws_creds

    set_aws_creds(aws_profile_name, verbose=True)

    s3_client = boto3.client("s3")
    upload_to_s3(s3_client=s3_client,
                 bucket_name=var_bucket_name,
                 local_path=var_local_path,
                 is_directory=var_directory_flag,
                 s3_key=var_s3_key)

else:
    aws_access_key_id = input("Enter your AWS Access Key ID: ")
    aws_secret_access_key = input("Enter your AWS Secret Access Key: ")
    aws_session_token = input("Enter your AWS Session Token: [Default: None]: ") or None

    s3_client = boto3.client("s3"
                             , aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             aws_session_token=aws_session_token)

    upload_to_s3(s3_client=s3_client,
                 bucket_name=var_bucket_name,
                 local_path=var_local_path,
                 is_directory=var_directory_flag,
                 s3_key=var_s3_key)


