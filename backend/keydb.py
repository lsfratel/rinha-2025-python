import os

from redis import Redis

keydb = Redis.from_url(
    os.getenv("KEYDB_URL", "redis://localhost:6379"),
)
