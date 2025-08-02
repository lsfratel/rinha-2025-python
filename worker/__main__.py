import os
import signal
import time
from datetime import datetime, timezone

import gevent
import msgpack
import requests
from gevent.lock import Semaphore
from gevent.pool import Pool
from requests.adapters import HTTPAdapter

from backend.keydb import keydb

PROCESSORS = {
    "default": {
        "health": True,
        "url": os.getenv("DEFAULT_PAYMENT_URL", "http://localhost:8001"),
    },
    "fallback": {
        "health": True,
        "url": os.getenv("FALLBAK_PAYMENT_URL", "http://localhost:8002"),
    },
}

HEALTH_CHECK_INTERVAL = 5
last_health_check = 0
health_lock = Semaphore()
pool = Pool(size=int(os.getenv("WORKER_POOL_SIZE", "250")))
running = True


def create_sessions():
    for processor in PROCESSORS.values():
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=int(os.getenv("HTTP_POOL_CONNECTIONS", "20")),
            pool_maxsize=int(os.getenv("HTTP_POOL_MAXSIZE", "100")),
            max_retries=0,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        processor["session"] = session


def get_health(processor: str) -> bool:
    with health_lock:
        return PROCESSORS[processor]["health"]


def set_health(processor: str, health: bool):
    with health_lock:
        PROCESSORS[processor]["health"] = health


def check_health(now: float = None):
    global last_health_check
    now = now or time.time()

    if (now - last_health_check) < HEALTH_CHECK_INTERVAL:
        return

    tasks = {
        name: gevent.spawn(
            info["session"].get,
            f"{info['url']}/payments/service-health",
        )
        for name, info in PROCESSORS.items()
    }

    gevent.joinall(tasks.values())

    for name, greenlet in tasks.items():
        try:
            resp = greenlet.value
            healthy = resp.status_code == 200 and not resp.json().get("failing", False)
            set_health(name, healthy)
        except Exception:
            set_health(name, False)

    last_health_check = now


def get_processor():
    check_health()

    if get_health("default"):
        return "default"

    if get_health("fallback"):
        return "fallback"

    gevent.sleep(0.1)
    return "default"


def store_payment(payment: dict, processor: str, timestamp: float):
    key = f"payment:{processor}:{payment['correlationId']}"
    pipe = keydb.pipeline()

    pipe.set(
        key,
        msgpack.packb(
            {"processor": processor, **payment},
            use_bin_type=True,
        ),
    )
    pipe.zadd("payments", {key: timestamp})

    pipe.execute()


def process_payment(payment: dict):
    processor = get_processor()
    url = PROCESSORS[processor]["url"]
    session = PROCESSORS[processor]["session"]
    dt = datetime.now(timezone.utc)

    try:
        resp = session.post(
            f"{url}/payments",
            json={**payment, "requestedAt": dt.isoformat()},
        )

        if resp.status_code != 200:
            raise Exception(f"Erro HTTP: {resp.status_code}")

        store_payment(payment, processor, dt.timestamp())
    except Exception:
        set_health(processor, False)
        alt_processor = "fallback" if processor == "default" else "default"
        if get_health(alt_processor):
            pool.spawn(process_payment, payment)
        else:
            keydb.rpush("queue:payments", msgpack.packb(payment, use_bin_type=True))


def handle_sigint(signum, frame):
    global running
    print("[SIGNAL] SIGINT received, terminating...")
    running = False


def handle_sigterm(signum, frame):
    global running
    print("[SIGNAL] SIGTERM received, terminating...")
    running = False


def worker_loop():
    print("[Worker] Starting main loop...")
    while running:
        try:
            result = keydb.blpop("queue:payments", timeout=2)
            if result:
                _, payment_data = result
                payment = msgpack.unpackb(payment_data, raw=False)
                pool.spawn(process_payment, payment)
        except Exception as e:
            print(f"[ERROR] Loop of worker: {e}")
            gevent.sleep(1)

    print("[Worker] Closing, waiting for tasks to finish...")
    pool.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        create_sessions()
        worker_loop()
    except KeyboardInterrupt:
        pass
