import base64
import json
import os

import boto3
from mypy_boto3_secretsmanager.client import SecretsManagerClient

from utility.log import get_logger

logger = get_logger(__name__)

class Secrets:
    """get secrets for API jira, tempo, openai from secretmanager or default environment variable"""
    def __init__(self, is_secret_manager: bool):
        if is_secret_manager:
            logger.debug("fetching configuration from awssecrets")
            session = boto3.session.Session()
            client: SecretsManagerClient = session.client(service_name="secretsmanager", region_name="ca-central-1")
            response = client.get_secret_value(SecretId="my-quiver")
            secret = json.loads(response["SecretString"])
            self._quiverquant_api_token = base64.b64decode(secret.get("QUIVERQUANT_API_TOKEN")).decode("utf-8")
        else:
            logger.debug("fetching configuration from env variables")
            self._quiverquant_api_token = base64.b64decode(os.getenv("QUIVERQUANT_API_TOKEN")).decode("utf-8")

    @property
    def quiverquant_api_token(self):
        return self._quiverquant_api_token
