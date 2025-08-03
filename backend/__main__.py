import os

import bjoern

from .config import Config
from .wsgi import create_app

if __name__ == "__main__":
    if Config.UNIX_SOCKET:
        if os.path.exists(Config.UNIX_SOCKET):
            os.remove(Config.UNIX_SOCKET)
        print(f"[Server] Listening on unix:{Config.UNIX_SOCKET}.")
        bjoern.run(create_app(), f"unix:{Config.UNIX_SOCKET}")
    else:
        print("[Server] Listening on port 9999.")
        bjoern.run(create_app(), "0.0.0.0", 9999)
