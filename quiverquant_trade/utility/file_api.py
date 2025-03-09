import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from utility.log import get_logger
from utility.my_quiver import build_congress_rep_list_from_json

ENV_TYPE = os.getenv("ENV_TYPE", "local")  # aws or local

HISTORY_FILE_NAME = "congress_history.json"

log = get_logger(__name__)

class HistoryFileAPI:
    def __init__(self):
        if ENV_TYPE == "local":
            self.history_path = Path(__file__).parent / ".." / ".." / "resources" / HISTORY_FILE_NAME
            log.debug(f"get history data from local {self.history_path.resolve()}")
            if self.history_path.exists():
                with open(self.history_path, "r") as file:
                    self._history_congress_dict = { congress_trade.uuid:congress_trade for congress_trade in build_congress_rep_list_from_json(json.load(file))}
            else:
                log.warning(f"file {self.history_path.resolve()} does not exists")
                self._history_congress_dict = {}

        elif ENV_TYPE == "aws":
            try:
                self.s3_client = boto3.client('s3')
                self.bucket = "quiver-inside-trade"
                self.key = f"quiver/api/congress/history/{HISTORY_FILE_NAME}"

                log.debug(f"get history data from s3 bucket={self.bucket}, key={self.key}")

                self.s3_object = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
                s3_content = self.s3_object['Body'].read().decode('utf-8')

                self._history_congress_dict = {
                    congress_trade.uuid: congress_trade
                    for congress_trade in build_congress_rep_list_from_json(json.loads(s3_content))
                }
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == "NoSuchKey":
                    log.warning(f"S3 key not found: bucket={self.bucket}, key={self.key}")
                else:
                    log.warning(f"AWS S3 ClientError: {error_code}", exc_info=True)
                self._history_congress_dict = {}
        else:
            raise NotImplemented(f"ENV_TYPE={ENV_TYPE} not implemented")

    @property
    def history_congress_dict(self):
        return self._history_congress_dict

    @history_congress_dict.setter
    def history_congress_dict(self, value):
        self._history_congress_dict = value

    def update_history(self, history_data):
        data_to_write = [congress_rep.get_all_fields_in_str_as_dict() for congress_rep in history_data.values()]
        match ENV_TYPE:
            case "local":
                with open(self.history_path, 'w') as file:
                    json.dump(data_to_write, file)
                    log.debug(f"history data updated to local {self.history_path.resolve()}")
            case "aws":
                self.s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=json.dumps(data_to_write))
                log.debug(f"history data updated to s3 bucket={self.bucket}, key={self.key}")
