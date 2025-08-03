import traceback
from datetime import UTC, datetime

import gevent
import msgpack
import redis
import requests
from requests.adapters import HTTPAdapter

from .confg import Config

redis = redis.StrictRedis(
    connection_pool=redis.ConnectionPool.from_url(
        Config.KEYDB_URL,
        max_connections=Config.NUM_WORKERS,
    ),
)

processors = (
    ("default", Config.DEFAULT_PAYMENT_URL),
    ("fallback", Config.FALLBACK_PAYMENT_URL),
)


def get_sesstion():
    adapter = HTTPAdapter(
        pool_connections=Config.NUM_WORKERS,
        pool_maxsize=Config.NUM_WORKERS,
    )
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def store_payment(payment: dict, processor: str, timestamp: float):
    key = f"payment:{processor}:{payment['correlationId']}"
    pipe = redis.pipeline(transaction=False)
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
    requested_at = datetime.now(UTC)
    timestamp = requested_at.timestamp()
    payload = {
        **payment,
        "requestedAt": requested_at.isoformat(),
    }
    for processor, url in processors:
        resp = session.post(f"{url}/payments", json=payload)
        if resp.status_code == 200:
            store_payment(payment, processor, timestamp)
            return
    gevent.sleep(0.5)
    process_payment(payment, session)


def worker():
    session = get_sesstion()
    while True:
        try:
            _, payment_data = redis.brpop("queue:payments", timeout=0)
            payment = msgpack.unpackb(payment_data, raw=False)
            process_payment(payment, session)
        except requests.HTTPError:
            print("[Worker] Unexpected HTTPError:")
            traceback.print_exc()
        except Exception:
            print("[Worker] Unexpected error:")
            traceback.print_exc()
        gevent.sleep(0.05)


if __name__ == "__main__":
    print("[Worker] Starting workers...")
    gevent.joinall(
        [gevent.spawn(worker) for _ in range(Config.NUM_WORKERS)],
    )
