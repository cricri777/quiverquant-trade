import json
import pathlib
from datetime import datetime, timedelta

from utility import log
from utility.file_api import HistoryFileAPI
from utility.my_quiver import MyQuiver, \
    build_congress_rep_list_from_json
from utility.notification import Notification
from utility.secrets import Secrets

RESOURCES_PATH = pathlib.Path(__file__).parent / ".." / "resources"
log = log.get_logger(__name__)


def run(is_secret_manager=False):
    """
    Algo:
        - read history trade
        - get new input trade
        - if there are new trade send notification
    :return:
    """
    log.debug("get congress inside trading from quiver api")
    secret = Secrets(is_secret_manager)
    congress_trading_json = MyQuiver(token=secret.quiverquant_api_token).congress_trading()
    new_congress_rep_list = build_congress_rep_list_from_json(
        congress_trading_json,
        (
            lambda rep: rep.report_date > (datetime.now() - timedelta(days=20))
                            and rep.amount > 100000
                            and str(rep.transaction).lower() == "purchase"
        )
    )
    new_congress_dict = { congress_rep.uuid:congress_rep for congress_rep in new_congress_rep_list}

    file_api = HistoryFileAPI()
    history_data = file_api.history_congress_dict

    new_congress_list = []
    for key, value in new_congress_dict.items():
        if key not in history_data:
            log.debug(f"record not found in history, adding to notification and history: [{json.dumps(value.get_all_fields_in_str_as_dict())}]")
            new_congress_list.append(value)
            history_data[key] = value

    if len(new_congress_list) > 0:
        log.debug(f"ship [{len(new_congress_list)}] records in notification")
        notification = Notification(new_congress_list)
        notification.send_email_via_ses()

        log.debug("update history with newer input")
        file_api.update_history(history_data)

    else:
        log.debug("no new trade received")


if __name__ == '__main__':
    run()