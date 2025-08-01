import bjoern

from .wsgi import create_app

if __name__ == "__main__":
    print("[Server] Listening on port 9999...")
    bjoern.run(create_app(), "0.0.0.0", 9999)
