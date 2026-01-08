# packages/api_utils/fetch.py
import logging
from .client import get_json
from .parser import log_first_item_keys

def fetch_data_from_api(api_endpoint: str):
    data = get_json(api_endpoint)
    logging.info("Successfully fetched API data")
    log_first_item_keys(data)
    return data