from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

from configuration.openapi import LoginSuccess, LogoutRequest, LogoutSuccess, UNAUTHORIZED
from user.serializers.user import GetUserByIdSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = GetUserByIdSerializer(self.user).data
        return data


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        operation_id='login',
        summary='Login',
        description=(
            'Public. Send username and password. '
            'The response has access, refresh, and the user. '
            'Later calls use Authorization: Bearer <access_token>.'
        ),
        auth=[],
        responses={
            200: LoginSuccess,
            401: OpenApiResponse(description='No active account was found for that username and password.'),
        },
    )
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        operation_id='refresh_token',
        summary='Refresh access token',
        description=(
            'Public. Send the refresh token from login. Returns a new access token. '
            'An invalid, expired, or logged-out refresh token returns 401.'
        ),
        auth=[],
    )
)
class RefreshView(TokenRefreshView):
    pass


class LogoutView(APIView):
    """Blacklist the refresh token so it cannot mint a new access token."""

    @extend_schema(
        tags=['Authentication'],
        operation_id='logout',
        summary='Logout',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Send the refresh token so it cannot be used again.'
        ),
        request=LogoutRequest,
        responses={
            200: LogoutSuccess,
            400: OpenApiResponse(description='The refresh token is missing, invalid, expired, or belongs to another user.'),
            401: UNAUTHORIZED,
        },
    )
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response(
                {'refresh': ['Refresh token is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token_user_id = token.payload.get('user_id')
            if str(token_user_id) != str(request.user.pk):
                return Response(
                    {'refresh': ['This refresh token does not belong to the logged-in user.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token.blacklist()
        except TokenError:
            return Response(
                {'refresh': ['Refresh token is invalid, expired, or already logged out.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Logged out successfully.'})
