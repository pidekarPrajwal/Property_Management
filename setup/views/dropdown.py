from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from configuration.openapi import (
    INVALID,
    PAGE_PARAM,
    PAGE_SIZE_PARAM,
    SEARCH_PARAM,
    listed,
)
from setup.models import Area, District, Project, Region, Site, State
from setup.serializers.dropdown import DropdownOptionSerializer
from setup.views.base import id_filter
from user.hierarchy import visible_queryset
from utils.pagination import Pagination

DROPDOWN_TYPES = ('state', 'region', 'district', 'area', 'project', 'site')

TYPE_PARAM = OpenApiParameter(
    name='type',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    enum=list(DROPDOWN_TYPES),
    description=(
        'Which dropdown to fill. state returns only states. '
        'region returns only regions, and so on for district, area, project, and site.'
    ),
)


def _option(record_id, name):
    return {
        'id': record_id,
        'name': name,
    }


def _search(queryset, search, *fields):
    if not search:
        return queryset
    query = Q()
    for field in fields:
        query |= Q(**{f'{field}__icontains': search})
    return queryset.filter(query).distinct()


class DropdownView(APIView):
    """One list for a frontend select, limited to the logged-in head's branch."""

    @extend_schema(
        tags=['Dropdown'],
        operation_id='get_dropdown',
        summary='Dropdown options',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Pass type=state to list only states. '
            'Pass type=region and state to list only regions in that state. '
            'Pass type=district and region (or state) to list only those districts. '
            'Pass type=area and district (or region, or state) to list only those areas. '
            'Pass type=project and area (or a parent above it) to list only those projects. '
            'Pass type=site and project (or a parent above it) to list only those sites. '
            'Each option is id and name.'
        ),
        parameters=[
            TYPE_PARAM,
            OpenApiParameter(
                name='state',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Limit region, district, area, project, or site options to this state.',
            ),
            OpenApiParameter(
                name='region',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Limit district, area, project, or site options to this region.',
            ),
            OpenApiParameter(
                name='district',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Limit area, project, or site options to this district.',
            ),
            OpenApiParameter(
                name='area',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Limit project or site options to this area.',
            ),
            OpenApiParameter(
                name='project',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Limit site options to this project.',
            ),
            SEARCH_PARAM,
            PAGE_PARAM,
            PAGE_SIZE_PARAM,
        ],
        responses={**listed(DropdownOptionSerializer), 400: INVALID},
    )
    def get(self, request):
        kind = (request.query_params.get('type') or '').strip().lower()
        if kind not in DROPDOWN_TYPES:
            raise ValidationError({'type': 'Use state, region, district, area, project, or site.'})
        search = (request.query_params.get('search') or '').strip()
        queryset = {
            'state': self._states,
            'region': self._regions,
            'district': self._districts,
            'area': self._areas,
            'project': self._projects,
            'site': self._sites,
        }[kind](request, search)
        paginator = Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        options = [_option(record.id, record.name) for record in page]
        return paginator.get_paginated_response(DropdownOptionSerializer(options, many=True).data)

    def _states(self, request, search):
        return _search(
            visible_queryset(request.user, State.objects.all()),
            search,
            'name',
            'code',
        )

    def _regions(self, request, search):
        queryset = visible_queryset(request.user, Region.objects.all())
        queryset = id_filter(queryset, 'state', request.query_params.get('state'), 'state_id')
        return _search(queryset, search, 'name', 'code')

    def _districts(self, request, search):
        queryset = visible_queryset(request.user, District.objects.all())
        queryset = id_filter(queryset, 'region', request.query_params.get('region'), 'region_id')
        queryset = id_filter(queryset, 'state', request.query_params.get('state'), 'region__state_id')
        return _search(queryset, search, 'name', 'code')

    def _areas(self, request, search):
        queryset = visible_queryset(request.user, Area.objects.all())
        queryset = id_filter(queryset, 'district', request.query_params.get('district'), 'district_id')
        queryset = id_filter(queryset, 'region', request.query_params.get('region'), 'district__region_id')
        queryset = id_filter(
            queryset, 'state', request.query_params.get('state'), 'district__region__state_id'
        )
        return _search(queryset, search, 'name', 'code')

    def _projects(self, request, search):
        queryset = visible_queryset(request.user, Project.objects.all())
        queryset = id_filter(queryset, 'area', request.query_params.get('area'), 'area_id')
        queryset = id_filter(queryset, 'district', request.query_params.get('district'), 'area__district_id')
        queryset = id_filter(
            queryset, 'region', request.query_params.get('region'), 'area__district__region_id'
        )
        queryset = id_filter(
            queryset, 'state', request.query_params.get('state'), 'area__district__region__state_id'
        )
        return _search(queryset, search, 'name', 'code', 'phase', 'contractor')

    def _sites(self, request, search):
        queryset = visible_queryset(request.user, Site.objects.all())
        queryset = id_filter(queryset, 'project', request.query_params.get('project'), 'project_id')
        queryset = id_filter(queryset, 'area', request.query_params.get('area'), 'area_id')
        queryset = id_filter(queryset, 'district', request.query_params.get('district'), 'area__district_id')
        queryset = id_filter(
            queryset, 'region', request.query_params.get('region'), 'area__district__region_id'
        )
        queryset = id_filter(
            queryset, 'state', request.query_params.get('state'), 'area__district__region__state_id'
        )
        return _search(queryset, search, 'name', 'code', 'address')
