from django.contrib.auth import get_user_model
from django.db.models import ProtectedError, Q
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied, ValidationError

from configuration.openapi import (
    ID_PARAM,
    USER_LIST_PARAMS,
    created,
    deleted,
    listed,
    one,
    updated,
)

from setup.views.base import RecordViewSet, id_filter
from user.designations import Designation
from user.hierarchy import can_manage_designation, outside_scope_message, visible_queryset
from user.serializers.user import (
    CreateUserSerializer,
    GetUserByIdSerializer,
    GetUserSerializer,
    UpdateUserSerializer,
)

User = get_user_model()

PROFILE_FIELDS = {'first_name', 'last_name', 'email', 'mobile_number', 'password'}


def _placement(validated_data, instance=None):
    def value(field):
        if field in validated_data:
            return validated_data[field]
        return getattr(instance, field, None)

    return (
        value('designation'),
        value('state'),
        value('region'),
        value('district'),
        value('area'),
        value('project'),
    )


def _reject_user_management(actor, designation, state, region, district, area, project):
    if not can_manage_designation(actor, designation):
        raise PermissionDenied('You can only manage users who are below your designation.')
    message = outside_scope_message(actor, state, region, district, area, project)
    if message:
        raise PermissionDenied(message)


class UserViewSet(RecordViewSet):
    queryset = User.objects.select_related('state', 'region', 'district', 'area', 'project').all()
    read_serializer_class = GetUserByIdSerializer

    def get_serializer_class(self):
        return {
            'create_user': CreateUserSerializer,
            'get_all_user': GetUserSerializer,
            'get_user_by_id': GetUserByIdSerializer,
            'update_user': UpdateUserSerializer,
        }.get(self.action, GetUserSerializer)

    def get_queryset(self):
        queryset = visible_queryset(self.request.user, super().get_queryset())
        designation = self.request.query_params.get('designation')
        if designation:
            if designation not in Designation.values:
                raise ValidationError({'designation': 'Unknown designation.'})
            queryset = queryset.filter(designation=designation)
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(mobile_number__icontains=search)
            )
        state = self.request.query_params.get('state')
        if state:
            queryset = id_filter(queryset, 'state', state, 'state_id')
        for param, lookup in (
            ('region', 'region_id'),
            ('district', 'district_id'),
            ('area', 'area_id'),
            ('project', 'project_id'),
        ):
            raw_value = self.request.query_params.get(param)
            if raw_value:
                queryset = id_filter(queryset, param, raw_value, lookup)
        return queryset

    @extend_schema(
        tags=['User'],
        operation_id='create_user',
        summary='Add user',
        description=(
            'Create a user below your designation and inside your hierarchy. '
            'Password is required. Requires Authorization: Bearer <access_token>.'
        ),
        request=CreateUserSerializer,
        responses=created(GetUserByIdSerializer),
    )
    def create_user(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['User'],
        operation_id='get_all_user',
        summary='Get users',
        description='List users this account is allowed to see.',
        parameters=USER_LIST_PARAMS,
        responses=listed(GetUserSerializer),
    )
    def get_all_user(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['User'],
        operation_id='get_user_by_id',
        summary='Get user by id',
        parameters=[ID_PARAM],
        responses=one(GetUserByIdSerializer),
    )
    def get_user_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['User'],
        operation_id='update_user',
        summary='Update user',
        description=(
            'PUT replaces the fields you send as a full update. PATCH changes only the fields you send. '
            'You can only change your own name, email, mobile number, and password. '
            'You can change another user only if they are below you and inside your hierarchy.'
        ),
        parameters=[ID_PARAM],
        request=UpdateUserSerializer,
        responses=updated(GetUserByIdSerializer),
    )
    def update_user(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['User'],
        operation_id='delete_user',
        summary='Delete user',
        description='You cannot delete your own account.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_user(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        designation, state, region, district, area, project = _placement(serializer.validated_data)
        _reject_user_management(
            self.request.user, designation, state, region, district, area, project
        )
        serializer.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        actor = self.request.user
        if actor.pk == instance.pk:
            blocked = set(serializer.validated_data) - PROFILE_FIELDS
            if blocked:
                raise PermissionDenied(
                    'You can only change your own name, email, mobile number, and password.'
                )
            serializer.save()
            return

        designation, state, region, district, area, project = _placement(
            serializer.validated_data, instance
        )
        _reject_user_management(
            actor,
            instance.designation,
            instance.state,
            instance.region,
            instance.district,
            instance.area,
            instance.project,
        )
        _reject_user_management(actor, designation, state, region, district, area, project)
        serializer.save()

    def perform_destroy(self, instance):
        actor = self.request.user
        if actor.pk == instance.pk:
            raise PermissionDenied('You cannot delete your own account.')
        _reject_user_management(
            actor,
            instance.designation,
            instance.state,
            instance.region,
            instance.district,
            instance.area,
            instance.project,
        )
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {'detail': 'This user cannot be deleted because other records still use this account.'}
            )
