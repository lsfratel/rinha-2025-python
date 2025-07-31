import os
from datetime import datetime, timezone

import requests
from huey import RedisHuey

from backend.services import keydb

PROCESSORS = {
    "default": os.getenv("DEFAULT_PAYMENT_URL", "http://localhost:8001"),
    "fallback": os.getenv("FALLBAK_PAYMENT_URL", "http://localhost:8002"),
}

PROCESSORS_ORDER = {
    "default": "fallback",
    "fallback": "default",
}

huey = RedisHuey(results=False, host=os.getenv('KEYDB_HOST', 'localhost'))

@huey.task()
def process_payment(payment: dict, processor="default"):
    dt = datetime.now(tz=timezone.utc)

    resp = requests.post(
        f"{PROCESSORS[processor]}/payments",
        json={**payment, "requestedAt": dt.isoformat()},
    )

    if resp.status_code != 200:
        process_payment(payment, PROCESSORS_ORDER[processor])
    else:
        keydb.store_payments(payment, dt.timestamp(), processor)
