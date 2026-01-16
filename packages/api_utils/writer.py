# packages/api_utils/writer.py

import json
import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

def write_data_to_jsonl(data: Iterable[dict], file_path: Path) -> None:
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = list(data)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")

    logger.info("Wrote %s records to %s", len(records), output_path)