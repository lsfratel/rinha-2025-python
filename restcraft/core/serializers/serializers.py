from typing import Any

from ..exceptions import ValidationError
from .fields import Field


class SerializerMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        attrs["__fields__"] = fields
        return super().__new__(cls, name, bases, attrs)


class Serializer(metaclass=SerializerMeta):
    def __init__(self, data: dict = None, instance: Any = None, context: dict = None):
        self.initial_data = data
        self.instance = instance
        self.context = context or {}
        self._validated_data = None
        self._errors = {}

        self.fields: dict[str, Field] = {}
        self._field_cache: dict[str, str] = {}

        for name, field in self.__fields__.items():
            field.bind(name)
            self.fields[name] = field
            self._field_cache[name] = field.name

    def is_valid(self) -> bool:
        if self.initial_data is None:
            self._errors = {"non_field_errors": ["No data provided."]}
            return False
        validated_data = {}
        errors = {}
        for field_name, field in self.fields.items():
            source_name = field.name
            if source_name not in self.initial_data and not field.required:
                continue
            raw_value = self.initial_data.get(source_name, None)
            if raw_value is None and field.default is not None:
                raw_value = field.default
            try:
                validated_value = field.validate(raw_value)
                validated_data[field_name] = validated_value
            except ValidationError as e:
                errors.update(e.details)
        if errors:
            self._errors = errors
            return False
        self._validated_data = validated_data
        return True

    @property
    def validated_data(self) -> dict:
        if self._validated_data is None:
            raise AttributeError(
                "You must call `.is_valid()` before accessing `validated_data`."
            )
        return self._validated_data

    @property
    def errors(self) -> dict:
        return self._errors

    def to_representation(self, obj: Any = None) -> dict:
        obj = obj or self.instance
        if obj is None:
            return {}
        data = {}
        for field_name, source_name in self._field_cache.items():
            value = getattr(obj, source_name, None)
            data[field_name] = self.fields[field_name].to_representation(value)
        return data

    def data(self) -> dict:
        return self.to_representation()
