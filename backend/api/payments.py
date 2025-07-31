from restcraft.http import Request, jsonify
from restcraft.views import View
from tasks.payments import process_payment

from ..services import keydb
from .serializers import CreatePaymentsSerializer, FilterPaymentsSerializer


class PaymentsView(View):
    post_serializer = CreatePaymentsSerializer

    def post(self, _: Request):
        data, *_ = self.validated_data(True)
        process_payment(data)

        return jsonify(status_code=202)


class PaymentsSummaryView(View):
    get_serializer = FilterPaymentsSerializer

    def get(self, _: Request):
        data, *_ = self.validated_data(True)
        payments = keydb.get_payments(data["from_"], data["to"])

        return jsonify(payments, status_code=200)


class PaymentsPurgeView(View):
    def post(self, _: Request):
        keydb.purge_payments()

        return jsonify(status_code=200)
