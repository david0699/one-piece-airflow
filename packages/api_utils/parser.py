# packages/api_utils/parser.py
import logging
from typing import Any

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
            logging.info(f"Column {i}: {key}")
    else:
        logging.warning("Could not determine first item structure")