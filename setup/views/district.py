from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import (
    ID_PARAM,
    PAGE_PARAM,
    PAGE_SIZE_PARAM,
    REGION_FILTER,
    SEARCH_PARAM,
    STATE_FILTER,
    created,
    deleted,
    listed,
    one,
    updated,
)

from setup.models import District
from setup.serializers.district import (
    CreateDistrictSerializer,
    GetDistrictByIdSerializer,
    GetDistrictSerializer,
    UpdateDistrictSerializer,
)
from setup.views.base import HierarchyViewSet, id_filter
from user.hierarchy import can_modify_district, can_modify_region


class DistrictViewSet(HierarchyViewSet):
    queryset = District.objects.select_related('region__state').all()
    read_serializer_class = GetDistrictByIdSerializer

    def get_serializer_class(self):
        return {
            'create_district': CreateDistrictSerializer,
            'get_all_district': GetDistrictSerializer,
            'get_district_by_id': GetDistrictByIdSerializer,
            'update_district': UpdateDistrictSerializer,
        }.get(self.action, GetDistrictSerializer)

    def apply_filters(self, queryset):
        queryset = id_filter(queryset, 'region', self.request.query_params.get('region'), 'region_id')
        return id_filter(queryset, 'state', self.request.query_params.get('state'), 'region__state_id')

    @extend_schema(
        tags=['District'],
        operation_id='create_district',
        summary='Add district',
        description='A district must belong to a region you are allowed to change. Requires Authorization: Bearer <access_token>.',
        request=CreateDistrictSerializer,
        responses=created(GetDistrictByIdSerializer),
    )
    def create_district(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['District'],
        operation_id='get_all_district',
        summary='Get districts',
        parameters=[SEARCH_PARAM, PAGE_PARAM, PAGE_SIZE_PARAM, STATE_FILTER, REGION_FILTER],
        responses=listed(GetDistrictSerializer),
    )
    def get_all_district(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['District'],
        operation_id='get_district_by_id',
        summary='Get district by id',
        parameters=[ID_PARAM],
        responses=one(GetDistrictByIdSerializer),
    )
    def get_district_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['District'],
        operation_id='update_district',
        summary='Update district',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send.',
        parameters=[ID_PARAM],
        request=UpdateDistrictSerializer,
        responses=updated(GetDistrictByIdSerializer),
    )
    def update_district(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['District'],
        operation_id='delete_district',
        summary='Delete district',
        description='Delete is refused while areas still belong to this district.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_district(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        region = serializer.validated_data['region']
        if not can_modify_region(self.request.user, region):
            raise PermissionDenied('You can only add a district inside a region you manage.')
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        new_region = serializer.validated_data.get('region', serializer.instance.region)
        if (
            new_region.id != serializer.instance.region_id
            and not can_modify_region(self.request.user, new_region)
        ):
            raise PermissionDenied('You cannot move this district to that region.')
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_district(self.request.user, instance):
            raise PermissionDenied('You can view this district, but you cannot change it.')
