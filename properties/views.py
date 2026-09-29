from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.market_rate import calculate_current_market_rates
from properties.upsert import synchronize
from properties.xlsx_parser import XlsxFormatError, read_xlsx


class PropertyXlsxUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['Property'],
        operation_id='upload_property_xlsx',
        summary='Synchronize properties from an XLSX file',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Send the workbook as multipart form field file. '
            'Each row is matched on property_id. '
            'Only columns present in the workbook are written. '
            'current_market_rate, owner_name, status, created_at, and updated_at '
            'are left unchanged unless that column is in the file. '
            'Missing properties are not deleted. '
            'Pass dry_run=true to count changes without saving them.'
        ),
        parameters=[
            OpenApiParameter(
                name='dry_run',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='When true, validate and count rows without saving.',
            ),
        ],
        request={'multipart/form-data': {'type': 'object', 'properties': {'file': {'type': 'string', 'format': 'binary'}}}},
        responses={200: dict, 400: dict},
    )
    def post(self, request):
        uploaded = request.FILES.get('file')
        if uploaded is None:
            return Response({'file': ['Upload the workbook in the file field.']}, status=status.HTTP_400_BAD_REQUEST)
        dry_run = str(request.query_params.get('dry_run', '')).lower() in ('1', 'true', 'yes')
        try:
            parsed = read_xlsx(uploaded)
        except XlsxFormatError as exc:
            return Response({'file': [str(exc)]}, status=status.HTTP_400_BAD_REQUEST)
        result = synchronize(parsed, uploaded.name, dry_run)
        return Response(result)


class CalculateMarketRateView(APIView):
    @extend_schema(
        tags=['Property'],
        operation_id='calculate_current_market_rate',
        summary='Calculate current market rate from nearby properties',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'This is separate from the XLSX upload. '
            'It sets current_market_rate from the average market_rate of other properties '
            'inside the search radius. No other column is changed.'
        ),
        parameters=[
            OpenApiParameter(
                name='radius_km',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Search radius in kilometres. Defaults to 2.',
            ),
        ],
        responses={200: dict},
    )
    def post(self, request):
        raw = request.query_params.get('radius_km')
        result = calculate_current_market_rates(raw if raw not in (None, '') else None)
        return Response(result)
