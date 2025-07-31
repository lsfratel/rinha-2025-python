import inspect
from typing import Any

from .exceptions import ValidationError


class Field:
    """Campo base para o serializer."""

    def __init__(self, required: bool = True, default: Any = None, name: str = None):
        self.required = required
        self.default = default
        self.name = name

    def validate(self, value: Any) -> Any:
        if value is None and self.required:
            raise ValidationError(
                {self.name or self.field_name: ["Este campo é obrigatório."]}
            )
        return value

    def to_representation(self, value: Any) -> Any:
        return value

    def bind(self, field_name: str):
        """Associa o nome do campo ao próprio campo."""
        self.field_name = field_name


class IntegerField(Field):
    def validate(self, value: Any) -> int:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                {self.name or self.field_name: ["Valor deve ser um inteiro."]}
            ) from e


class FloatField(Field):
    def validate(self, value: Any) -> int:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                {self.name or self.field_name: ["Valor deve ser um ponto flutuante."]}
            ) from e


class StringField(Field):
    def __init__(
        self,
        required: bool = True,
        default: str = None,
        max_length: int = None,
        name: str = None,
    ):
        super().__init__(required, default, name)
        self.max_length = max_length

    def validate(self, value: Any) -> str:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        if not isinstance(value, str):
            raise ValidationError({self.field_name: ["Valor deve ser uma string."]})
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                {
                    self.name or self.field_name: [
                        f"Não pode ter mais que {self.max_length} caracteres."
                    ]
                }
            )
        return value


class BooleanField(Field):
    def validate(self, value: Any) -> bool:
        super().validate(value)
        if value is None:
            return self.default if self.default is not None else None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower()
            if value in ("true", "1", "yes", "on"):
                return True
            if value in ("false", "0", "no", "off"):
                return False
        raise ValidationError(
            {self.name or self.field_name: ["Valor deve ser booleano."]}
        )


class ListField(Field):
    def __init__(self, child: Field = None, **kwargs):
        super().__init__(**kwargs)
        self.child = child

    def validate(self, value: Any) -> list:
        super().validate(value)
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValidationError(
                {self.name or self.field_name: ["Valor deve ser uma lista."]}
            )
        if self.child:
            validated = []
            for item in value:
                try:
                    validated.append(self.child.validate(item))
                except ValidationError as e:
                    # Erros de itens individuais podem ser detalhados
                    raise ValidationError(
                        {self.name or self.field_name: [f"Erro no item: {e}"]}
                    ) from e
            return validated
        return value

    def to_representation(self, value: list) -> list:
        if self.child and value:
            return [self.child.to_representation(item) for item in value]
        return value


class Serializer:
    """Serializer base."""

    def __init__(self, data: dict = None, instance: Any = None, context: dict = None):
        self.initial_data = data
        self.instance = instance
        self.context = context or {}
        self._validated_data = None
        self._errors = {}

        # Bind fields
        self.fields = {}
        for name, field in self.get_fields().items():
            field.bind(name)
            self.fields[name] = field

    def get_fields(self) -> dict[str, Field]:
        """Retorna um dicionário de campos do serializer."""
        fields = {}
        for key, value in inspect.getmembers(self.__class__):
            if isinstance(value, Field):
                fields[key] = value
        return fields

    def is_valid(self) -> bool:
        """Valida os dados e retorna True se válido."""
        if self.initial_data is None:
            self._errors = {"non_field_errors": ["Nenhum dado fornecido."]}
            return False

        validated_data = {}
        errors = {}

        for field_name, field in self.fields.items():
            try:
                raw_value = self.initial_data.get(field.name or field_name, None)
                # Se não estiver presente e for obrigatório, pode falhar
                if raw_value is None and field.required:
                    raw_value = field.default
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
        """Retorna os dados validados. Disponível apenas após is_valid()."""
        if self._validated_data is None:
            raise AttributeError(
                "Você deve chamar `.is_valid()` antes de acessar `validated_data`."
            )
        return self._validated_data

    @property
    def errors(self) -> dict:
        """Retorna os erros de validação."""
        return self._errors

    def to_representation(self, obj: Any = None) -> dict:
        """Serializa o objeto (ou instância) para um dicionário."""
        obj = obj or self.instance
        if obj is None:
            return {}

        data = {}
        for field_name, field in self.fields.items():
            value = getattr(obj, field_name, None)
            data[field_name] = field.to_representation(value)
        return data

    def data(self) -> dict:
        """Retorna os dados serializados (para resposta)."""
        return self.to_representation()
