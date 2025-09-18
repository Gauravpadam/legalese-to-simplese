import logging
import os

import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

log = logging.getLogger(__name__)
aws_client = None
kb_client = None

def get_aws_bedrock_client(region_name: str = "us-west-2"):
    global aws_client
    if aws_client is not None:
        log.debug("Using existing AWS client.")
        return aws_client

    log.debug("Creating a new AWS client.")
    try:
        # Get AWS credentials from environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        aws_region = os.getenv('AWS_DEFAULT_REGION', region_name)
        
        # Create client with explicit credentials
        client_kwargs = {
            "service_name": "bedrock-runtime",
            "region_name": aws_region,
            "verify": False
        }
        
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs.update({
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key
            })
            if aws_session_token:
                client_kwargs["aws_session_token"] = aws_session_token
            log.debug("Using explicit AWS credentials from environment variables.")
        else:
            log.debug("Using default AWS credential chain (no explicit credentials found in environment).")
        
        client = boto3.client(**client_kwargs)
        aws_client = client
        log.debug("AWS client created successfully.")
        return aws_client
    except Exception as e:
        log.error(f"Failed to create AWS client: {e}")
        raise Exception

def get_aws_bedrock_kb_client(region_name: str = "us-west-2"):
    global kb_client
    if kb_client is not None:
        log.debug("Using existing AWS client.")
        return kb_client

    log.debug("Creating a new AWS client.")
    try:
        # Get AWS credentials from environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        aws_region = os.getenv('AWS_DEFAULT_REGION', region_name)
        
        # Create client with explicit credentials
        client_kwargs = {
            "service_name": "bedrock-agent-runtime",
            "region_name": aws_region,
            "verify": False
        }
        
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs.update({
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key
            })
            if aws_session_token:
                client_kwargs["aws_session_token"] = aws_session_token
            log.debug("Using explicit AWS credentials from environment variables.")
        else:
            log.debug("Using default AWS credential chain (no explicit credentials found in environment).")
        
        client = boto3.client(**client_kwargs)
        kb_client = client
        log.debug("AWS client created successfully.")
        return kb_client
    except Exception as e:
        log.error(f"Failed to create AWS client: {e}")
        raise Exception