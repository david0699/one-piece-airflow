# packages/api_utils/fetch.py
import logging
from .client import get_json
from .parser import log_first_item_keys, simplify_raw_data

logger = logging.getLogger(__name__)

def fetch_data_from_api(api_endpoint: str, timeout: int = 10) -> list[dict]:
    raw_data = get_json(api_endpoint, timeout=timeout)
    logger.info("Successfully fetched API data")
    data = simplify_raw_data(raw_data)
    logger.info("Simplified raw data as list of dicts")
    log_first_item_keys(data)
    return data