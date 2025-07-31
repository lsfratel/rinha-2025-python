from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .request import Request


def jsonify(body="", status_code=200, headers=None):
    nheaders = headers or {}

    nheaders.update({"content-type": "application/json"})

    nbody = b""

    if body != "":
        nbody = json.dumps(body).encode()

    return status_code, nheaders, nbody


def on_exception(_: Request, ex: Exception):
    status_code = getattr(ex, "status", 500)
    details, *_ = ex.args
    return jsonify({"details": details}, status_code=status_code)
