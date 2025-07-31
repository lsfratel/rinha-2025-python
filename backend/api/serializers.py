from restcraft.core import serializer


class CreatePaymentsSerializer(serializer.Serializer):
    correlationId = serializer.StringField()
    amount = serializer.FloatField()


class FilterPaymentsSerializer(serializer.Serializer):
    from_ = serializer.StringField(name="from", default="2000-01-01T00:00:00.000Z")
    to = serializer.StringField(default="2030-01-01T00:00:00.000Z")
