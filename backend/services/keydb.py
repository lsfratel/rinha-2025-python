import json
import os

from redis import Redis

from ..utils import iso_to_unix

db = Redis(
    host=os.getenv("KEYDB_HOST", "redis"),
    port=int(os.getenv("KEYDB_PORT", "6379")),
)


def store_payments(data: dict, timestamp: float, processor: str):
    key = f"payment:{processor}:{data['correlationId']}"
    pipe = db.pipeline()

    pipe.set(key, json.dumps({"processor": processor, **data}))
    pipe.zadd("payments", {key: timestamp})

    pipe.execute()


def get_payments(from_: str, to: str):
    keys = db.zrangebyscore("payments", min=iso_to_unix(from_), max=iso_to_unix(to))

    data = {
        "default": {"totalRequests": 0, "totalAmount": 0},
        "fallback": {"totalRequests": 0, "totalAmount": 0},
    }

    if not keys:
        return data

    for k in db.mget(keys):
        if not k:
            continue
        payment = json.loads(k)
        data[payment["processor"]]["totalAmount"] += payment["amount"]
        data[payment["processor"]]["totalRequests"] += 1

    data["default"]["totalAmount"] = round(data["default"]["totalAmount"], 2)
    data["fallback"]["totalAmount"] = round(data["fallback"]["totalAmount"], 2)

    return data


def purge_payments():
    keys = db.zrange("payments", 0, -1)

    pipe = db.pipeline()

    if keys:
        pipe.delete(*keys)

    pipe.delete("payments")

    pipe.execute()
