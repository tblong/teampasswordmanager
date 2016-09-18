# passwords-to-s3

This script exports all TPM passwords to an AWS S3 bucket.  Python `v2.7.11` was used to test this script.


# Setup Steps
1. Ensure the following python packages are installed:
    - requests: `pip install requests`
    - boto3: `pip install boto3`
2. Place `tpmPasswordsToS3.py` and `tpmPasswordsToS3Config.sample` inside the same directory
3. Rename `tpmPasswordsToS3Config.sample` to `tpmPasswordsToS3Config.py`
4. Setup AWS Items:
    - Create S3 bucket
    - S3 bucket policy
    - IAM credentials and access keys
5. Setup a read-only user for all projects in TPM
    - encode `user:pass` to base64 for next step
6. Configure all settings inside `tpmPasswordsToS3Config.py`
7. Schedule execution of `tpmPasswordsToS3.py` using `cron` or `task scheduler`
