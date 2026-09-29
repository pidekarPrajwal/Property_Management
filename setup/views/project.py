from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

from configuration.openapi import (
    AREA_FILTER,
    DISTRICT_FILTER,
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

from setup.models import Project
from setup.serializers.project import (
    CreateProjectSerializer,
    GetProjectByIdSerializer,
    GetProjectSerializer,
    UpdateProjectSerializer,
)
from setup.views.base import HierarchyViewSet, id_filter
from user.hierarchy import can_modify_area, can_modify_project


class ProjectViewSet(HierarchyViewSet):
    queryset = Project.objects.select_related('area__district__region__state').all()
    read_serializer_class = GetProjectByIdSerializer
    search_fields = ('name', 'code', 'phase', 'contractor')

    def get_serializer_class(self):
        return {
            'create_project': CreateProjectSerializer,
            'get_all_project': GetProjectSerializer,
            'get_project_by_id': GetProjectByIdSerializer,
            'update_project': UpdateProjectSerializer,
        }.get(self.action, GetProjectSerializer)

    def apply_filters(self, queryset):
        queryset = id_filter(queryset, 'area', self.request.query_params.get('area'), 'area_id')
        queryset = id_filter(queryset, 'district', self.request.query_params.get('district'), 'area__district_id')
        queryset = id_filter(
            queryset, 'region', self.request.query_params.get('region'), 'area__district__region_id'
        )
        return id_filter(
            queryset,
            'state',
            self.request.query_params.get('state'),
            'area__district__region__state_id',
        )

    @extend_schema(
        tags=['Project'],
        operation_id='create_project',
        summary='Add project',
        description='A project must belong to an area you are allowed to change. Requires Authorization: Bearer <access_token>.',
        request=CreateProjectSerializer,
        responses=created(GetProjectByIdSerializer),
    )
    def create_project(self, request):
        return self.create_record(request)

    @extend_schema(
        tags=['Project'],
        operation_id='get_all_project',
        summary='Get projects',
        parameters=[
            SEARCH_PARAM,
            PAGE_PARAM,
            PAGE_SIZE_PARAM,
            STATE_FILTER,
            REGION_FILTER,
            DISTRICT_FILTER,
            AREA_FILTER,
        ],
        responses=listed(GetProjectSerializer),
    )
    def get_all_project(self, request):
        return self.list_records(request)

    @extend_schema(
        tags=['Project'],
        operation_id='get_project_by_id',
        summary='Get project by id',
        parameters=[ID_PARAM],
        responses=one(GetProjectByIdSerializer),
    )
    def get_project_by_id(self, request):
        return self.record_by_id(request)

    @extend_schema(
        tags=['Project'],
        operation_id='update_project',
        summary='Update project',
        description='PUT replaces the fields you send as a full update. PATCH changes only the fields you send.',
        parameters=[ID_PARAM],
        request=UpdateProjectSerializer,
        responses=updated(GetProjectByIdSerializer),
    )
    def update_project(self, request):
        return self.update_record(request)

    @extend_schema(
        tags=['Project'],
        operation_id='delete_project',
        summary='Delete project',
        description='Delete is refused while sites or users still belong to this project.',
        parameters=[ID_PARAM],
        responses=deleted(),
    )
    def delete_project(self, request):
        return self.delete_record(request)

    def perform_create(self, serializer):
        area = serializer.validated_data['area']
        if not can_modify_area(self.request.user, area):
            raise PermissionDenied('You can only add a project inside an area you manage.')
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_can_change(serializer.instance)
        new_area = serializer.validated_data.get('area', serializer.instance.area)
        if new_area.id != serializer.instance.area_id and not can_modify_area(self.request.user, new_area):
            raise PermissionDenied('You cannot move this project to that area.')
        serializer.save()

    def ensure_can_change(self, instance):
        if not can_modify_project(self.request.user, instance):
            raise PermissionDenied('You can view this project, but you cannot change it.')
