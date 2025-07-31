import io
import json
from typing import Any
from urllib.parse import parse_qs


class Request:
    def __init__(self, environ: dict[str, str]):
        self.ENV = environ

    @property
    def body(self) -> dict[str, Any]:
        if self.method not in ("POST", "PUT", "PATCH"):
            raise Exception("Method must be POST, PUT or PATCH.")

        if self.content_length and not self.content_type:
            raise Exception("Missing headers, content type must be present.")

        if hasattr(self, "__body__"):
            return self.__body__

        content_type = self.content_type
        content_length = self.content_length
        stream = self.ENV.get("wsgi.input", io.BytesIO())

        if content_type == "application/x-www-form-urlencoded":
            parsed = parse_qs(
                stream.read(content_length).decode(), keep_blank_values=True
            )
            self.__body__ = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        elif content_type == "application/json":
            self.__body__ = json.loads(stream.read(content_length).decode())
        else:
            raise Exception("Content type not supported.")

        return self.__body__

    @property
    def path_params(self) -> dict[str, str]:
        return getattr(self, "__params__", {})

    @path_params.setter
    def path_params(self, params: dict[str, str]):
        self.__params__ = params

    @property
    def method(self):
        return self.ENV.get("REQUEST_METHOD", "GET")

    @property
    def path(self):
        return self.ENV.get("PATH_INFO", "/")

    @property
    def query_params(self):
        if hasattr(self, "__qs__"):
            return self.__qs__

        if not (qs_raw := self.ENV.get("QUERY_STRING")):
            return {}

        parsed = parse_qs(qs_raw, keep_blank_values=True)

        self.__qs__ = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        return self.__qs__

    @property
    def headers(self):
        if hasattr(self, "__headers__"):
            return self.__headers__

        self.__headers__ = {
            key[5:].replace("_", "-").lower(): value
            for key, value in self.ENV.items()
            if key.startswith("HTTP_")
        }

        return self.__headers__

    @property
    def content_type(self):
        return self.ENV.get("CONTENT_TYPE")

    @property
    def content_length(self):
        return int(self.ENV.get("CONTENT_LENGTH", 0) or 0)
