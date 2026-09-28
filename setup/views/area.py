from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import (
    DISTRICT_FILTER,
    ID_PARAM,
    REGION_FILTER,
    SEARCH_PARAM,
    STATE_FILTER,
    created,
    deleted,
    listed,
    one,
    updated,
)

from setup.models import Area
from setup.serializers.area import (
    CreateAreaSerializer,
    GetAreaByIdSerializer,
    GetAreaSerializer,
    UpdateAreaSerializer,
)
from setup.views.base import HierarchyViewSet, id_filter
from user.hierarchy import can_modify_area, can_modify_district


class AreaViewSet(HierarchyViewSet):
    queryset = Area.objects.select_related('district__region__state').all()
    read_serializer_class = GetAreaByIdSerializer

    def get_serializer_class(self):
        return {
            'create_area': CreateAreaSerializer,
            'get_all_area': GetAreaSerializer,
            'get_area_by_id': GetAreaByIdSerializer,
            'update_area': UpdateAreaSerializer,
        }.get(self.action, GetAreaSerializer)

    def apply_filters(self, queryset):
        queryset = id_filter(queryset, 'district', self.request.query_params.get('district'), 'district_id')
        queryset = id_filter(queryset, 'region', self.request.query_params.get('region'), 'district__region_id')
        return id_filter(
            queryset, 'state', self.request.query_params.get('state'), 'district__region__state_id'
        )

    @extend_schema(
        tags=['Area'],
        operation_id='create_area',
        summary='Add area',
        description='An area must belong to a district you are allowed to change. Requires Authorization: Bearer <access_token>.',
        request=CreateAreaSerializer,
        responses=created(GetAreaByIdSerializer),
    )
    def create_area(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['Area'],
        operation_id='get_all_area',
        summary='Get areas',
        parameters=[SEARCH_PARAM, STATE_FILTER, REGION_FILTER, DISTRICT_FILTER],
        responses=listed(GetAreaSerializer),
    )
    def get_all_area(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['Area'],
        operation_id='get_area_by_id',
        summary='Get area by id',
        parameters=[ID_PARAM],
        responses=one(GetAreaByIdSerializer),
    )
    def get_area_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['Area'],
        operation_id='update_area',
        summary='Update area',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send.',
        parameters=[ID_PARAM],
        request=UpdateAreaSerializer,
        responses=updated(GetAreaByIdSerializer),
    )
    def update_area(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['Area'],
        operation_id='delete_area',
        summary='Delete area',
        description='Delete is refused while projects or sites still belong to this area.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_area(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        district = serializer.validated_data['district']
        if not can_modify_district(self.request.user, district):
            raise PermissionDenied('You can only add an area inside a district you manage.')
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        new_district = serializer.validated_data.get('district', serializer.instance.district)
        if (
            new_district.id != serializer.instance.district_id
            and not can_modify_district(self.request.user, new_district)
        ):
            raise PermissionDenied('You cannot move this area to that district.')
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_area(self.request.user, instance):
            raise PermissionDenied('You can view this area, but you cannot change it.')
