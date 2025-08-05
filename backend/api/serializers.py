from restcraft.core import serializers


class CreatePaymentsSerializer(serializers.Serializer):
    correlation_id = serializers.StringField(source_name="correlationId")
    amount = serializers.FloatField()


class FilterPaymentsSerializer(serializers.Serializer):
    from_ = serializers.StringField(default="2000-01-01T00:00:00.000Z", source_name="from")
    to = serializers.StringField(default="2030-01-01T00:00:00.000Z")
