import os
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def env(key: str, default: Any = None, parse: Callable[[str], T] = str) -> T:
    return parse(os.getenv(key, default))


class Config:
    DEFAULT_PAYMENT_URL = env("DEFAULT_PAYMENT_URL", "http://localhost:8001")
    FALLBACK_PAYMENT_URL = env("FALLBACK_PAYMENT_URL", "http://localhost:8002")

    KEYDB_URL = env("KEYDB_URL", "redis://localhost")

    NUM_WORKERS = env("NUM_WORKERS", "30", int)
