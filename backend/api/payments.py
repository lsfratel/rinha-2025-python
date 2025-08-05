from restcraft.http import Request, jsonify
from restcraft.views import View

from ..services import payment
from .serializers import CreatePaymentsSerializer, FilterPaymentsSerializer


class PaymentsSummaryView(View):

    query_params_serializer = FilterPaymentsSerializer

    def get(self, _: Request):
        data, *_ = self.validated_query_params(True)
        payments = payment.get_payments(data["from_"], data["to"])
        return jsonify(payments, status_code=200)


class PaymentsView(View):

    body_serializer = CreatePaymentsSerializer

    def post(self, _: Request):
        data, *_ = self.validated_body(True)
        payment.enqueue_payment(data)
        return jsonify(status_code=202)


class PaymentsPurgeView(View):

    def post(self, _: Request):
        payment.purge_payments()
        return jsonify(status_code=200)
