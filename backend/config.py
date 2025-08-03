import os
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def env(key: str, default: Any = None, parse: Callable[[str], T] = str) -> T:
    return parse(os.getenv(key, default))


class Config:
    KEYDB_URL = env("KEYDB_URL", "redis://localhost")
    UNIX_SOCKET = env("UNIX_SOCKET")
