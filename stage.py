from dotenv import load_dotenv
from os import getenv
import boto3
from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher
from os import listdir, path

load_dotenv()

provider = InstanceMetadataProvider(
    iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2)
)
credentials = provider.load().get_frozen_credentials()
client = boto3.client(
    "s3",
    region_name=getenv("AWS_REGION"),
    aws_access_key_id=credentials.access_key,
    aws_secret_access_key=credentials.secret_key,
    aws_session_token=credentials.token,
)
data_dir, bucket = getenv("SEED_DIR"), getenv("S3_BUCKET")
for file_name in listdir(data_dir):
    file_path = path.join(data_dir, file_name)
    client.upload_file(file_path, bucket, file_path)
