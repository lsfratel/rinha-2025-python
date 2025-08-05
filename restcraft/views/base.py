from typing import Any

from ..core.exceptions import ValidationError
from ..http import Request


class View:
    """"""

    query_params_serializer = ...
    body_serializer = ...

    @property
    def ctx(self):
        return self.__ctx__

    @ctx.setter
    def ctx(self, ctx: dict[str, Any]):
        self.__ctx__ = ctx

    @property
    def request(self) -> Request:
        return self.ctx["request"]

    def get_data(self) -> dict[str, Any]:
        if self.request.method in ("POST", "PUT", "PATCH"):
            return self.request.body
        else:
            return self.request.query_params

    def validated_query_params(self, raise_=False):
        if serializer := getattr(self, "query_params_serializer", None):
            instance = serializer(data=self.request.query_params)
            is_valid = instance.is_valid()
            if raise_ and not is_valid:
                raise ValidationError(instance.errors)
            return instance.validated_data, instance.errors
        return self.request.query_params, None

    def validated_body(self, raise_=False):
        if serializer := getattr(self, "body_serializer", None):
            instance = serializer(data=self.request.body)
            is_valid = instance.is_valid()
            if raise_ and not is_valid:
                raise ValidationError(instance.errors)
            return instance.validated_data, instance.errors
        return self.request.body, None
