from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import (
    ID_PARAM,
    PAGE_PARAM,
    PAGE_SIZE_PARAM,
    SEARCH_PARAM,
    STATE_FILTER,
    created,
    deleted,
    listed,
    one,
    updated,
)

from setup.models import Region
from setup.serializers.region import (
    CreateRegionSerializer,
    GetRegionByIdSerializer,
    GetRegionSerializer,
    UpdateRegionSerializer,
)
from setup.views.base import HierarchyViewSet, id_filter
from user.hierarchy import can_modify_region, can_modify_state


class RegionViewSet(HierarchyViewSet):
    queryset = Region.objects.select_related('state').all()
    read_serializer_class = GetRegionByIdSerializer

    def get_serializer_class(self):
        return {
            'create_region': CreateRegionSerializer,
            'get_all_region': GetRegionSerializer,
            'get_region_by_id': GetRegionByIdSerializer,
            'update_region': UpdateRegionSerializer,
        }.get(self.action, GetRegionSerializer)

    def apply_filters(self, queryset):
        return id_filter(queryset, 'state', self.request.query_params.get('state'), 'state_id')

    @extend_schema(
        tags=['Region'],
        operation_id='create_region',
        summary='Add region',
        description='A region must belong to a state you are allowed to change. Requires Authorization: Bearer <access_token>.',
        request=CreateRegionSerializer,
        responses=created(GetRegionByIdSerializer),
    )
    def create_region(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['Region'],
        operation_id='get_all_region',
        summary='Get regions',
        description='List regions inside this account\'s hierarchy.',
        parameters=[SEARCH_PARAM, PAGE_PARAM, PAGE_SIZE_PARAM, STATE_FILTER],
        responses=listed(GetRegionSerializer),
    )
    def get_all_region(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['Region'],
        operation_id='get_region_by_id',
        summary='Get region by id',
        parameters=[ID_PARAM],
        responses=one(GetRegionByIdSerializer),
    )
    def get_region_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['Region'],
        operation_id='update_region',
        summary='Update region',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send. The region cannot be moved outside your hierarchy.',
        parameters=[ID_PARAM],
        request=UpdateRegionSerializer,
        responses=updated(GetRegionByIdSerializer),
    )
    def update_region(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['Region'],
        operation_id='delete_region',
        summary='Delete region',
        description='Delete is refused while districts still belong to this region.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_region(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        state = serializer.validated_data['state']
        if not can_modify_state(self.request.user, state):
            raise PermissionDenied('You can only add a region inside a state you manage.')
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        new_state = serializer.validated_data.get('state', serializer.instance.state)
        if new_state.id != serializer.instance.state_id and not can_modify_state(self.request.user, new_state):
            raise PermissionDenied('You cannot move this region to that state.')
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_region(self.request.user, instance):
            raise PermissionDenied('You can view this region, but you cannot change it.')
