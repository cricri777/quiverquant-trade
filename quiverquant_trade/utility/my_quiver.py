import json
from datetime import datetime
from typing import List

from utility.log import get_logger
import requests

log = get_logger(__name__)

class CongressRepresentative:
    def __init__(self, representative, bio_guide_id, report_date, transaction_date, ticker, transaction, _range, house,
                 amount, party, last_modified, ticker_type, description, excess_return, price_change, spy_change):
        self.representative = representative
        self.bio_guide_id = bio_guide_id
        self.report_date = datetime.strptime(report_date, "%Y-%m-%d")
        self.transaction: str = transaction
        self.ticker = ticker
        self.transaction_date = datetime.strptime(transaction_date, "%Y-%m-%d")
        self.range = _range
        self.house = house
        self.amount = float(amount) if amount else None
        self.party = party
        self.last_modified = datetime.strptime(last_modified, "%Y-%m-%d")
        self.ticker_type = ticker_type
        self.description = description
        self.excess_return = float(excess_return) if excess_return else None
        self.price_change = float(price_change) if price_change else None
        self.spy_change = float(spy_change) if spy_change else None

        # build a uuid
        uuid_fiels = [
            self.representative,
            self.bio_guide_id,
            self.report_date.strftime("%Y-%m-%d"),
            self.transaction_date.strftime("%Y-%m-%d"),
            self.ticker,
            self.transaction,
            self.range,
            self.house,
            self.party,
            self.last_modified.strftime("%Y-%m-%d"),
            self.ticker_type
        ]

        self.uuid = hash(",".join(uuid_fiels))

    def get_all_fields_in_str_as_dict(self) -> dict:
        return {
            "UUID": self.uuid,
            "Representative": self.representative,
            "BioGuideID": self.bio_guide_id,
            "ReportDate": self.report_date.strftime("%Y-%m-%d"),
            "TransactionDate": self.transaction_date.strftime("%Y-%m-%d"),
            "Ticker": self.ticker,
            "Transaction": self.transaction,
            "Range": self.range,
            "House": self.house,
            "Amount": self.amount,
            "Party": self.party,
            "last_modified": self.last_modified.strftime("%Y-%m-%d"),
            "TickerType": self.ticker_type,
            "Description": self.description,
            "ExcessReturn": self.excess_return,
            "PriceChange": self.price_change,
            "SPYChange": self.spy_change,
        }


def build_congress_rep_list_from_json(json_array, filter_condition=None) -> List[CongressRepresentative]:
    """
    Build a filtered list of CongressRepresentative from a json_array based on a filter condition.

    :param json_array: The source JSON array to process.
    :param filter_condition: A lambda (or function) defining the filter condition. Defaults to None.
                             If None, no filtering is applied, and all representatives are included.
    """
    filtered_congress_reps: List[CongressRepresentative] = []
    for json_object in json_array:
        congress_rep = CongressRepresentative(
            representative=json_object.get("Representative", None),
            bio_guide_id=json_object.get("BioGuideID", None),
            report_date=json_object.get("ReportDate", None),
            transaction=json_object.get("Transaction", None),
            ticker=json_object.get("Ticker", None),
            transaction_date=json_object.get("TransactionDate", None),
            _range=json_object.get("Range", None),
            house=json_object.get("House", None),
            amount=json_object.get("Amount", None),
            party=json_object.get("Party", None),
            last_modified=json_object.get("last_modified", None),
            ticker_type=json_object.get("TickerType", None),
            description=json_object.get("Description", None),
            excess_return=json_object.get("ExcessReturn", None),
            price_change=json_object.get("PriceChange", None),
            spy_change=json_object.get("SPYChange", None),
        )

        # Apply the filter condition if provided, otherwise include all entities
        if filter_condition is None or filter_condition(congress_rep):
            filtered_congress_reps.append(congress_rep)

    return filtered_congress_reps



class MyQuiver:
    def __init__(self, token):
        self.token = token
        self.headers = {'accept': 'application/json',
                        'Authorization': "Token " + self.token}

    def congress_trading(self, ticker="", politician=False, recent=True):
        if recent:
            url_start = 'https://api.quiverquant.com/beta/live/congresstrading'
        else:
            url_start = 'https://api.quiverquant.com/beta/bulk/congresstrading'
        if politician:
            ticker = ticker.replace(" ", "%20")
            url = url_start + "?representative=" + ticker

        elif len(ticker) > 0:
            url_start = 'https://api.quiverquant.com/beta/historical/congresstrading'
            url = url_start + "/" + ticker
        else:
            url = url_start
        log.debug(f"quiverquant api url={url}")
        r = requests.get(url, headers=self.headers)
        return json.loads(r.content)
