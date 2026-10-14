import json
import logging
from datetime import datetime

from app.core import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("erp_assistant")


def log_request(record):
    record = {"time": datetime.now().isoformat(timespec="seconds"), **record}

    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    usage = record["usage"]
    logger.info(
        "user=%s route=%s docs=%s tokens=%d in/%d out/%d emb cost=$%.5f latency=%dms",
        record["user_id"], record["route"], record["documents_retrieved"],
        usage["input_tokens"], usage["output_tokens"], usage["embedding_tokens"],
        usage["cost_usd"], record["latency_ms"],
    )
