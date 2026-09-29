from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import (
    AREA_FILTER,
    DISTRICT_FILTER,
    ID_PARAM,
    PAGE_PARAM,
    PAGE_SIZE_PARAM,
    PROJECT_FILTER,
    REGION_FILTER,
    SEARCH_PARAM,
    STATE_FILTER,
    created,
    deleted,
    listed,
    one,
    updated,
)

from setup.models import Site
from setup.serializers.site import (
    CreateSiteSerializer,
    GetSiteByIdSerializer,
    GetSiteSerializer,
    UpdateSiteSerializer,
)
from setup.views.base import HierarchyViewSet, id_filter
from user.designations import Designation
from user.hierarchy import can_create_site, can_modify_site


class SiteViewSet(HierarchyViewSet):
    queryset = Site.objects.select_related(
        'area__district__region__state',
        'project',
        'created_by',
    ).all()
    read_serializer_class = GetSiteByIdSerializer
    search_fields = ('name', 'code', 'address')

    def get_serializer_class(self):
        return {
            'create_site': CreateSiteSerializer,
            'get_all_site': GetSiteSerializer,
            'get_site_by_id': GetSiteByIdSerializer,
            'update_site': UpdateSiteSerializer,
        }.get(self.action, GetSiteSerializer)

    def apply_filters(self, queryset):
        queryset = id_filter(queryset, 'area', self.request.query_params.get('area'), 'area_id')
        queryset = id_filter(queryset, 'project', self.request.query_params.get('project'), 'project_id')
        queryset = id_filter(queryset, 'district', self.request.query_params.get('district'), 'area__district_id')
        queryset = id_filter(queryset, 'region', self.request.query_params.get('region'), 'area__district__region_id')
        return id_filter(
            queryset,
            'state',
            self.request.query_params.get('state'),
            'area__district__region__state_id',
        )

    @extend_schema(
        tags=['Site'],
        operation_id='create_site',
        summary='Add site',
        description=(
            'Only an Area Head can create a site, and only inside their own area, '
            'for a project in that area. Send latitude and longitude as lists with one number per polygon point. '
            'Requires Authorization: Bearer <access_token>.'
        ),
        request=CreateSiteSerializer,
        responses=created(GetSiteByIdSerializer),
    )
    def create_site(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['Site'],
        operation_id='get_all_site',
        summary='Get sites',
        parameters=[
            SEARCH_PARAM,
            PAGE_PARAM,
            PAGE_SIZE_PARAM,
            STATE_FILTER,
            REGION_FILTER,
            DISTRICT_FILTER,
            AREA_FILTER,
            PROJECT_FILTER,
        ],
        responses=listed(GetSiteSerializer),
    )
    def get_all_site(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['Site'],
        operation_id='get_site_by_id',
        summary='Get site by id',
        parameters=[ID_PARAM],
        responses=one(GetSiteByIdSerializer),
    )
    def get_site_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['Site'],
        operation_id='update_site',
        summary='Update site',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send. A site cannot be moved outside your hierarchy.',
        parameters=[ID_PARAM],
        request=UpdateSiteSerializer,
        responses=updated(GetSiteByIdSerializer),
    )
    def update_site(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['Site'],
        operation_id='delete_site',
        summary='Delete site',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_site(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        area = serializer.validated_data['area']
        project = serializer.validated_data['project']
        if not can_create_site(self.request.user, area, project):
            if self.request.user.designation != Designation.AREA_HEAD:
                raise PermissionDenied('Only an Area Head can create a site.')
            raise PermissionDenied(
                'An Area Head can only create a site inside their own area, for a project in that area.'
            )
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        area = serializer.validated_data.get('area', serializer.instance.area)
        project = serializer.validated_data.get('project', serializer.instance.project)
        if not can_modify_site(self.request.user, area, project):
            raise PermissionDenied('You cannot move this site outside your hierarchy.')
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_site(self.request.user, instance.area, instance.project):
            raise PermissionDenied('You can view this site, but you cannot change it.')
