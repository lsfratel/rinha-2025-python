import os

from redis import ConnectionPool, StrictRedis

keydb = StrictRedis(
    connection_pool=ConnectionPool.from_url(
        os.getenv("KEYDB_URL", "redis://localhost:6379"),
        max_connections=50,
    ),
    protocol=3,
)
