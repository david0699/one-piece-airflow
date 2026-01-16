# packages/api_utils/parser.py
import logging
from typing import Any

logger = logging.getLogger(__name__)

def log_first_item_keys(data: Any) -> None:
    """
    Logs the keys of the first item in a typical API response.
    Supports:
    - list[dict]
    - {"data": list[dict]}
    """

    first_item = None

    if isinstance(data, list) and data:
        first_item = data[0]

    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value:
                first_item = value[0]
                break

    if isinstance(first_item, dict):
        for i, key in enumerate(first_item.keys()):
            logger.info(f"Column {i}: {key}")
    else:
        logger.warning("Could not determine first item structure")

def simplify_raw_data(data: Any) -> list[dict]:
    """
    Extracts a list of dicts from common API response formats.

    Supports:
    - list[dict]
    - {"data": list[dict]}

    Always returns a list (possibly empty).
    """

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    
    if isinstance(data, dict):
        data_list = data.get("data")
        if isinstance(data_list, list):
            return [item for item in data_list if isinstance(item, dict)]

    logger.warning("Unsupported data structure received: %s", type(data))
    return []