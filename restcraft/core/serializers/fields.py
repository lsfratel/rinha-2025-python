from collections.abc import Callable
from typing import Any

from ..exceptions import ValidationError


class Field:
    def __init__(
        self,
        required: bool = True,
        default: Any = None,
        source_name: Any = None,
        validators: list[Callable] = None,
    ):
        self.required = required
        self.default = default
        self.source_name = source_name
        self.field_name = None
        self.validators = validators or []

    @property
    def name(self) -> str:
        return self.source_name or self.field_name

    def validate(self, value: Any) -> Any:
        if value is None and self.required:
            raise ValidationError({self.name: ["This field is required."]})

        for validator in self.validators:
            value = validator(value)

        return value

    def to_representation(self, value: Any) -> Any:
        return value

    def bind(self, field_name: str):
        self.field_name = field_name


class IntegerField(Field):
    def validate(self, value: Any) -> int:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValidationError({self.name: ["Value must be an integer."]}) from e


class FloatField(Field):
    def validate(self, value: Any) -> float:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValidationError({self.name: ["Value must be a float."]}) from e


class StringField(Field):
    def __init__(self, max_length: int = None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def validate(self, value: Any) -> str:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        if not isinstance(value, str):
            raise ValidationError({self.name: ["Value must be a string."]})
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                {self.name: [f"Cannot be longer than {self.max_length} characters."]}
            )
        return value


class BooleanField(Field):
    _TRUE_VALUES = {"true", "1", "yes", "on"}
    _FALSE_VALUES = {"false", "0", "no", "off"}

    def validate(self, value: Any) -> bool:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower()
            if value in self._TRUE_VALUES:
                return True
            if value in self._FALSE_VALUES:
                return False
        raise ValidationError({self.name: ["Value must be boolean."]})


class ListField(Field):
    def __init__(self, child: Field = None, **kwargs):
        super().__init__(**kwargs)
        self.child = child

    def validate(self, value: Any) -> list:
        super().validate(value)
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValidationError({self.name: ["Value must be a list."]})
        if self.child:
            validated = []
            errors = []
            for i, item in enumerate(value):
                try:
                    validated.append(self.child.validate(item))
                except ValidationError as e:
                    errors.append(f"Error on item {i}: {e}")
            if errors:
                raise ValidationError({self.name: errors})
            return validated
        return value

    def to_representation(self, value: list) -> list:
        if value is None:
            return None
        if self.child and value:
            return [self.child.to_representation(item) for item in value]
        return value
