from restcraft.urls import path

from .payments import PaymentsPurgeView, PaymentsSummaryView, PaymentsView

urls = [
    path("/payments", PaymentsView),
    path("/payments-summary", PaymentsSummaryView),
    path("/purge-payments", PaymentsPurgeView),
]
