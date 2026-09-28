from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import ID_PARAM, SEARCH_PARAM, created, deleted, listed, one, updated

from setup.models import State
from setup.serializers.state import (
    CreateStateSerializer,
    GetStateByIdSerializer,
    GetStateSerializer,
    UpdateStateSerializer,
)
from setup.views.base import HierarchyViewSet
from user.hierarchy import can_modify_state, is_global_access


class StateViewSet(HierarchyViewSet):
    queryset = State.objects.all()
    read_serializer_class = GetStateByIdSerializer

    def get_serializer_class(self):
        return {
            'create_state': CreateStateSerializer,
            'get_all_state': GetStateSerializer,
            'get_state_by_id': GetStateByIdSerializer,
            'update_state': UpdateStateSerializer,
        }.get(self.action, GetStateSerializer)

    @extend_schema(
        tags=['State'],
        operation_id='create_state',
        summary='Add state',
        description='Create a state. Only CMD and Main Admin can do this. Requires Authorization: Bearer <access_token>.',
        request=CreateStateSerializer,
        responses=created(GetStateByIdSerializer),
    )
    def create_state(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['State'],
        operation_id='get_all_state',
        summary='Get states',
        description='List the states this account is allowed to see.',
        parameters=[SEARCH_PARAM],
        responses=listed(GetStateSerializer),
    )
    def get_all_state(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['State'],
        operation_id='get_state_by_id',
        summary='Get state by id',
        parameters=[ID_PARAM],
        responses=one(GetStateByIdSerializer),
    )
    def get_state_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['State'],
        operation_id='update_state',
        summary='Update state',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send.',
        parameters=[ID_PARAM],
        request=UpdateStateSerializer,
        responses=updated(GetStateByIdSerializer),
    )
    def update_state(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['State'],
        operation_id='delete_state',
        summary='Delete state',
        description='Delete is refused while regions still belong to this state.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_state(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        if not is_global_access(self.request.user):
            raise PermissionDenied('Only CMD and Main Admin can create a state.')
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_state(self.request.user, instance):
            raise PermissionDenied('You can view this state, but you cannot change it.')
