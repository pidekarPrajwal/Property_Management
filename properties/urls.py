from django.urls import path

from properties.views import CalculateMarketRateView, PropertyXlsxUploadView

urlpatterns = [
    path('properties/upload-xlsx/', PropertyXlsxUploadView.as_view(), name='upload-property-xlsx'),
    path(
        'properties/calculate-market-rate/',
        CalculateMarketRateView.as_view(),
        name='calculate-market-rate',
    ),
]
