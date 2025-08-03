from redis import ConnectionPool, StrictRedis

from .config import Config

if Config.KEYDB_URL.startswith("unix:"):
    from redis import UnixDomainSocketConnection

    keydb = StrictRedis(
        connection_pool=ConnectionPool(
            connection_class=UnixDomainSocketConnection,
            path=Config.KEYDB_URL.replace("unix:", ""),
            max_connections=Config.NUM_WORKERS,
        ),
        protocol=3,
    )
else:
    keydb = StrictRedis(
        connection_pool=ConnectionPool.from_url(
            Config.KEYDB_URL,
            max_connections=Config.NUM_WORKERS,
        ),
        protocol=3,
    )
