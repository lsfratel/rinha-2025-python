import os

import bjoern

from .wsgi import create_app

socket = os.getenv("UNIX_SOCKET", None)

if __name__ == "__main__":
    if socket:
        if os.path.exists(socket):
            os.remove(socket)
        print(f"[Server] Listening on unix:{socket}.")
        bjoern.run(create_app(), f"unix:{socket}")
    else:
        print("[Server] Listening on port 9999.")
        bjoern.run(create_app(), "0.0.0.0", 9999)
