import msgpack

from ..keydb import keydb
from ..utils import iso_to_unix


def get_payments(from_: str, to: str):
    keys = keydb.zrangebyscore("payments", min=iso_to_unix(from_), max=iso_to_unix(to))
    data = {
        "default": {"totalRequests": 0, "totalAmount": 0},
        "fallback": {"totalRequests": 0, "totalAmount": 0},
    }
    if not keys:
        return data
    for k in keydb.mget(keys):
        if not k:
            continue
        payment = msgpack.unpackb(k, raw=False)
        data[payment["processor"]]["totalAmount"] += payment["amount"]
        data[payment["processor"]]["totalRequests"] += 1
    data["default"]["totalAmount"] = round(data["default"]["totalAmount"], 2)
    data["fallback"]["totalAmount"] = round(data["fallback"]["totalAmount"], 2)
    return data


def enqueue_payment(payment: dict):
    keydb.rpush("queue:payments", msgpack.packb(payment, use_bin_type=True))


def purge_payments():
    keys = keydb.zrange("payments", 0, -1)
    pipe = keydb.pipeline()
    if keys:
        pipe.delete(*keys)
    pipe.delete("payments")
    pipe.execute()
