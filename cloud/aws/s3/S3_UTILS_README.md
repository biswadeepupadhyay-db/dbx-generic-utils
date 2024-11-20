### S3 Utilities

#### Upload local files to s3 bucket

##### prerequisite

To run the `upload_from_client` utility on your local you need to

1. install the aws-boto3 python package on your client using the command `pip3 install -U boto3`
2. Clone this repo to your client from where you plan on uploading files to s3 bucket.


##### Configuration

Before you can run the script you need to configure the inputs in the `.cloud/auth/s3/config/upload_files.json`

The config looks like below:
```json
{
  "auth_method" : "",
  "auth" : {
    "sso" : {
      "sso_profile_name" : "",
      "default_region" : ""
    },
    "access_keys" : {
      "access_key_id" : "",
      "secret_access_key" : "",
      "session_token" : ""
    }
  },
  "is_directory" : false,
  "local_files_path" : "",
  "bucket_name" : "",
  "s3_prefix" : ""
}
```

this utility uses two authentication mechanisms i.e using `SSO` & `access keys`.

###### SSO

If you plan on using sso for this utility make sure you have your sso configuration done using `aws-cli`on your client 
machine. Follow the details [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) to setup your 
sso profile.

Once your SSO Profile is configured, you can refer your `~/.aws/config` file to fetch and provide
 your SSO region & SSO profile name details below in the config file.
```json
{
  "auth_method" : "sso",
  "auth" : {
    "sso" : {
      "sso_profile_name" : "us-west-2",
      "default_region" : "your-sso-profile-name"
    },
    "access_keys" : {
      "access_key_id" : "",
      "secret_access_key" : "",
      "session_token" : ""
    }
  }
  ...
}
```

###### Access Keys

You can also use the AWS client Access keys as authentication method for this utility. This method is suitable
for automation & Scheduling. You may get your access keys i.e `aws_access_key_id` & `aws_secret_access_key`
from your AWS account console. If your administrator has set access key expiry session in that case
you will have to additionally pass the `aws_session_token` (optional) as well to the config file. Your
config should look like this below:

```json
{
  "auth_method" : "access_keys",
  "auth" : {
    "sso" : {
      "sso_profile_name" : "",
      "default_region" : ""
    },
    "access_keys" : {
      "access_key_id" : "your-aws-access-key-id",
      "secret_access_key" : "your-aws-secret-access-key",
      "session_token" : "your-aws-session-token-if-enabled"
    }
  }
  ...
}
```

Once the Authentication method is configured, you need to provide you local file & bucket details
on the config file.

If you plan on uploading a single file, in that case `is_directory` field needs to be set to `false`
whereas if you are planning on uploading an entire directory that contains several files, you need
to set this field to `true`.

Mention you local file/directory path against the field `local_files_path`. Mention s3 the bucket name 
under `bucket_name` and provide your s3 file url prefix under `s3_prefix` (optional). If you don't
configure any s3 prefix, all your files will be directly uploaded under your bucket root directory.

* A sample File upload config might look like below:
```json
{
  ...
  "is_directory" : false,
  "local_files_path" : "./path/to/your/file.csv",
  "bucket_name" : "s3-bucket",
  "s3_prefix" : "dev/solutions/raw"
}
```
the uploaded s3 file uri would look like `s3://<s3-bucket>/dev/solutions/raw/file.csv`.

* A sample Directory upload config might look like below:

```json
{
  ...
  "is_directory" : false,
  "local_files_path" : "./path/to/your/directory/",
  "bucket_name" : "s3-bucket",
  "s3_prefix" : "dev/solutions/raw"
}
```

the s3 uri for one of the files from that directory would look like `s3://<s3-bucket>/directory/dev/solutions/raw/file1.csv`.

##### Run the Utility

Once your configuration is done, run the below script from the home directory of tis cloned repo
on your client machine.

Assuming you have cloned this repo to `~/.dbx-generic-utils` folder:

1. go to the folder i.e `cd ~/.dbx-generic-utils`.
2. Run the command `python3 cloud/aws/s3/upload_from_client.py`.
