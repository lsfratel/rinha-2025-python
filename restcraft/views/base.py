from typing import Any

from ..core.exceptions import ValidationError
from ..http import Request


class View:
    @property
    def ctx(self):
        return self.__ctx__

    @ctx.setter
    def ctx(self, ctx: dict[str, Any]):
        self.__ctx__ = ctx

    def validated_data(
        self, raise_=False
    ) -> tuple[dict[str, Any], dict[str, list[str]]]:
        req: Request = self.ctx["request"]

        if req.method in ("POST", "PUT", "PATCH"):
            data = req.body
        else:
            data = req.query_params

        Serializer = getattr(self, f"{req.method.lower()}_serializer", None)

        if Serializer is None:
            raise Exception(f"Missing {req.method} serializer!.")

        serializer_instance = Serializer(data=data)

        if not serializer_instance.is_valid():
            if raise_:
                raise ValidationError(serializer_instance.errors)

            return {}, serializer_instance.errors

        return serializer_instance.validated_data, {}
