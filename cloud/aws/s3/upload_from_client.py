import os
import sys
import json
import getpass
import logging

import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = os.path.sep.join(SCRIPT_DIR.split(os.path.sep)[:-3])
sys.path.append(PYTHON_PATH)

from cloud.utils import read_json_file


CONFIG_PATH = f"{PYTHON_PATH}/cloud/aws/s3/config/upload_files.json" if len(sys.argv) == 1 else sys.argv[1]
UPLOAD_CONFIG = read_json_file(CONFIG_PATH)


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


def redact_input(prompt, redact_char='*', show_last_n=0):
    """
    Get input from user and return a redacted version.

    :param prompt: The prompt to display to the user
    :param redact_char: Character to use for redaction (default '*')
    :param show_last_n: Number of characters to show at the end (default 4)
    :return: Tuple of (original input, redacted input)
    """
    # Get input without showing it on the screen
    user_input = getpass.getpass(prompt)

    # Redact the input
    if len(user_input) <= show_last_n:
        redacted = redact_char * len(user_input)
    else:
        redacted = redact_char * (len(user_input) - show_last_n) + user_input[-show_last_n:]

    return user_input, redacted


var_auth_method = "access_keys" if not UPLOAD_CONFIG.get("auth_method", "").strip() else UPLOAD_CONFIG.get("auth_method", "").strip().lower()

var_local_path = UPLOAD_CONFIG.get("local_files_path", "").strip()
if not var_local_path:
    raise Exception("No local file/directory path specified. Mention the same in config file against `local_files_path`.")
var_directory_flag = False if not UPLOAD_CONFIG.get("is_directory", False) else True
var_bucket_name = UPLOAD_CONFIG.get("bucket_name", "")
if not var_bucket_name:
    raise Exception("No bucket name specified. Mention the same in config file against `bucket_name`.")
var_s3_key = UPLOAD_CONFIG.get("s3_prefix", "").strip()


if var_auth_method == "sso":
    AWS_DEFAULT_REGION = UPLOAD_CONFIG["auth"]["sso"]["default_region"] or "us-east-1"
    os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION
    aws_profile_name = UPLOAD_CONFIG["auth"]["sso"]["sso_profile_name"] or None
    if not aws_profile_name:
        raise ValueError("You must enter your AWS Profile Name under `auth.sso.sso_profile_name`.")
    from cloud.aws.auth.sso import set_aws_creds

    set_aws_creds(aws_profile_name, verbose=True)

    s3_client = boto3.client("s3")
    upload_to_s3(s3_client=s3_client,
                 bucket_name=var_bucket_name,
                 local_path=var_local_path,
                 is_directory=var_directory_flag,
                 s3_key=var_s3_key)

else:
    # aws_access_key_id, redacted_id = redact_input("Enter your AWS Access Key ID: ")
    # aws_secret_access_key, redacted_key = redact_input("Enter your AWS Secret Access Key: ")
    # aws_session_token, redacted_token = redact_input("Enter your AWS Session Token: [Default: None]: ") or None

    aws_access_key_id = UPLOAD_CONFIG["auth"]["access_keys"]["access_key_id"]
    aws_secret_access_key = UPLOAD_CONFIG["auth"]["access_keys"]["secret_access_key"]
    aws_session_token = UPLOAD_CONFIG["auth"]["access_keys"]["session_token"]

    if not aws_access_key_id or not aws_secret_access_key:
        raise Exception("Access keys are missing in the config file.")

    s3_client = boto3.client("s3"
                             , aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             aws_session_token=aws_session_token)

    upload_to_s3(s3_client=s3_client,
                 bucket_name=var_bucket_name,
                 local_path=var_local_path,
                 is_directory=var_directory_flag,
                 s3_key=var_s3_key)


