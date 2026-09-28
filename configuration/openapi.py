"""OpenAPI helpers only. These do not change request handling."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

from user.designations import Designation
from user.serializers.user import GetUserByIdSerializer


class BearerHeaderScheme(OpenApiAuthenticationExtension):
    """Authorize box value is sent as the Authorization header, unchanged."""

    target_class = 'rest_framework_simplejwt.authentication.JWTAuthentication'
    name = 'bearerAuth'
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter: Bearer <access_token>',
        }


ID_PARAM = OpenApiParameter(
    name='id',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=True,
    description='Record id. Update and delete also accept id in the JSON body.',
)

SEARCH_PARAM = OpenApiParameter(
    name='search',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=False,
    description='Case-insensitive search on the name.',
)

USER_SEARCH_PARAM = OpenApiParameter(
    name='search',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=False,
    description='Search username, first name, last name, email, or mobile number.',
)

DESIGNATION_PARAM = OpenApiParameter(
    name='designation',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=False,
    enum=[choice for choice, _label in Designation.choices],
    description='Filter users by designation.',
)


def _optional_id(name, description):
    return OpenApiParameter(
        name=name,
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=description,
    )


STATE_FILTER = _optional_id('state', 'Only records in this state.')
REGION_FILTER = _optional_id('region', 'Only records in this region.')
DISTRICT_FILTER = _optional_id('district', 'Only records in this district.')
AREA_FILTER = _optional_id('area', 'Only records in this area.')
PROJECT_FILTER = _optional_id('project', 'Only records in this project.')

USER_LIST_PARAMS = [
    USER_SEARCH_PARAM,
    DESIGNATION_PARAM,
    STATE_FILTER,
    REGION_FILTER,
    DISTRICT_FILTER,
    AREA_FILTER,
    PROJECT_FILTER,
]


def _error(text):
    return OpenApiResponse(description=text)


INVALID = _error('The body or the id is not valid, or a parent link does not match.')
UNAUTHORIZED = _error('Missing or invalid access token. Send Authorization: Bearer <access_token>.')
FORBIDDEN = _error('This account cannot do that, or the record is outside its hierarchy.')
NOT_FOUND = _error('No record with that id is visible to this account.')


def created(serializer):
    return {201: serializer, 400: INVALID, 401: UNAUTHORIZED, 403: FORBIDDEN}


def listed(serializer):
    return {200: serializer(many=True), 401: UNAUTHORIZED}


def one(serializer):
    return {200: serializer, 400: INVALID, 401: UNAUTHORIZED, 404: NOT_FOUND}


def updated(serializer):
    return {200: serializer, 400: INVALID, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND}


def removed():
    return {204: None, 400: INVALID, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND}


deleted = removed


LoginSuccess = inline_serializer(
    name='LoginSuccess',
    fields={
        'access': serializers.CharField(help_text='Access token. Send it as: Bearer <access_token>.'),
        'refresh': serializers.CharField(help_text='Refresh token. Use it to get a new access token or to log out.'),
        'user': GetUserByIdSerializer(),
    },
)

LogoutRequest = inline_serializer(
    name='LogoutRequest',
    fields={
        'refresh': serializers.CharField(help_text='Refresh token returned by login.'),
    },
)

LogoutSuccess = inline_serializer(
    name='LogoutSuccess',
    fields={
        'detail': serializers.CharField(),
    },
)
