import msgpack

from ..keydb import keydb
from ..utils import iso_to_unix


def get_payments(from_: str, to: str):
    members = keydb.zrangebyscore("payments", iso_to_unix(from_), iso_to_unix(to))
    data = {
        "default": {"totalRequests": 0, "totalAmount": 0},
        "fallback": {"totalRequests": 0, "totalAmount": 0},
    }
    for m in members:
        proc, amount, _ = m.decode().split(":", 2)
        data[proc]["totalRequests"] += 1
        data[proc]["totalAmount"] += float(amount)
    for k in data:
        data[k]["totalAmount"] = round(data[k]["totalAmount"], 2)
    return data


def enqueue_payment(payment: dict):
    keydb.rpush(
        "queue:payments",
        msgpack.packb(payment, use_bin_type=True),
    )


def purge_payments():
    keys = keydb.zrange("payments", 0, -1)
    pipe = keydb.pipeline()
    if keys:
        pipe.delete(*keys)
    pipe.delete("payments")
    pipe.execute()
