import traceback
from datetime import datetime, timezone

import gevent
import msgpack
import redis
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .confg import Config

redis = redis.StrictRedis(
    connection_pool=redis.ConnectionPool.from_url(
        Config.KEYDB_URL,
        max_connections=Config.NUM_WORKERS,
        decode_responses=False,
    ),
)


def get_sesstion():
    adapter = HTTPAdapter(
        pool_connections=Config.NUM_WORKERS,
        pool_maxsize=Config.NUM_WORKERS * 2,
        max_retries=Retry(
            total=Config.NUM_OF_RETRY,
            backoff_factor=Config.BACKOFF_FACTOR,
            allowed_methods={"POST"},
            status_forcelist={500},
        ),
    )

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def store_payment(payment: dict, processor: str, timestamp: float):
    key = f"payment:{processor}:{payment['correlationId']}"
    pipe = redis.pipeline()

    pipe.set(
        key,
        msgpack.packb(
            {"processor": processor, **payment},
            use_bin_type=True,
        ),
    )
    pipe.zadd("payments", {key: timestamp})

    pipe.execute()


def process_payment(payment: dict, session: requests.Session):
    requested_at = datetime.now(timezone.utc)
    timestamp = requested_at.timestamp()

    payload = {**payment, "requestedAt": requested_at.isoformat()}
    resp = session.post(f"{Config.DEFAULT_PAYMENT_URL}/payments", json=payload)

    resp.raise_for_status()

    store_payment(payment, "default", timestamp)


def worker():
    session = get_sesstion()

    while True:
        try:
            data = redis.brpop("queue:payments", timeout=1)
            if data:
                _, payment_data = data
                payment = msgpack.unpackb(payment_data, raw=False)
                process_payment(payment, session)
        except requests.HTTPError:
            traceback.print_exc()
        except Exception:
            pass


if __name__ == "__main__":
    print("[Worker] Starting...")
    gevent.joinall(
        [gevent.spawn(worker) for _ in range(Config.NUM_WORKERS)],
    )
