from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from configuration.openapi import FORBIDDEN, INVALID, UNAUTHORIZED
from setup.models import Area, District, Project, Region, Site, State
from setup.serializers.area import GetAreaSerializer
from setup.serializers.district import GetDistrictSerializer
from setup.serializers.project import GetProjectSerializer
from setup.serializers.region import GetRegionSerializer
from setup.serializers.site import GetSiteSerializer
from setup.serializers.state import GetStateSerializer
from user.designations import Designation
from user.hierarchy import visible_queryset
from user.models import User
from user.serializers.user import GetUserByIdSerializer, GetUserSerializer


HEAD_DESIGNATIONS = {
    Designation.CMD,
    Designation.MAIN_ADMIN,
    Designation.STATE_HEAD,
    Designation.REGION_HEAD,
    Designation.DISTRICT_HEAD,
    Designation.AREA_HEAD,
    Designation.PROJECT_HEAD,
}


class IsHead(BasePermission):
    """Dashboard is only for organisation heads. Each head still only receives their own branch."""

    message = 'Only a head can open the dashboard.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'designation', None) in HEAD_DESIGNATIONS
        )


def _head_place_ids(heads, field):
    return heads.exclude(**{f'{field}__isnull': True}).values_list(field, flat=True)


def apply_head_filter(designation, users, states, regions, districts, areas, projects, sites):
    """Keep the selected heads and the records under their own place.

    CMD and Main Admin have no single place, so their filter keeps those people
    and every place already visible to the caller.
    """
    heads = users.filter(designation=designation)
    if designation in (Designation.CMD, Designation.MAIN_ADMIN):
        return heads, states, regions, districts, areas, projects, sites

    if designation == Designation.STATE_HEAD:
        ids = _head_place_ids(heads, 'state_id')
        return (
            users.filter(state_id__in=ids),
            states.filter(id__in=ids),
            regions.filter(state_id__in=ids),
            districts.filter(region__state_id__in=ids),
            areas.filter(district__region__state_id__in=ids),
            projects.filter(area__district__region__state_id__in=ids),
            sites.filter(area__district__region__state_id__in=ids),
        )
    if designation == Designation.REGION_HEAD:
        ids = _head_place_ids(heads, 'region_id')
        return (
            users.filter(region_id__in=ids),
            states.none(),
            regions.filter(id__in=ids),
            districts.filter(region_id__in=ids),
            areas.filter(district__region_id__in=ids),
            projects.filter(area__district__region_id__in=ids),
            sites.filter(area__district__region_id__in=ids),
        )
    if designation == Designation.DISTRICT_HEAD:
        ids = _head_place_ids(heads, 'district_id')
        return (
            users.filter(district_id__in=ids),
            states.none(),
            regions.none(),
            districts.filter(id__in=ids),
            areas.filter(district_id__in=ids),
            projects.filter(area__district_id__in=ids),
            sites.filter(area__district_id__in=ids),
        )
    if designation == Designation.AREA_HEAD:
        ids = _head_place_ids(heads, 'area_id')
        return (
            users.filter(area_id__in=ids),
            states.none(),
            regions.none(),
            districts.none(),
            areas.filter(id__in=ids),
            projects.filter(area_id__in=ids),
            sites.filter(area_id__in=ids),
        )
    ids = _head_place_ids(heads, 'project_id')
    return (
        users.filter(project_id__in=ids),
        states.none(),
        regions.none(),
        districts.none(),
        areas.none(),
        projects.filter(id__in=ids),
        sites.filter(project_id__in=ids),
    )


def dashboard_designation(raw):
    if raw in (None, ''):
        return None
    key = str(raw).strip().upper().replace('-', '_').replace(' ', '_')
    if key not in HEAD_DESIGNATIONS:
        raise ValidationError({'designation': 'Select a valid designation.'})
    return key


class DashboardView(APIView):
    """One screen of data for the logged-in head, limited to their branch."""

    permission_classes = [IsHead]

    @extend_schema(
        tags=['Dashboard'],
        operation_id='get_dashboard',
        summary='Dashboard for the logged-in head',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'With no designation filter, returns everything this account is allowed to see. '
            'Pass designation=STATE_HEAD to return those state heads and the regions, districts, '
            'areas, projects, sites, and people under their states. '
            'REGION_HEAD, DISTRICT_HEAD, AREA_HEAD, and PROJECT_HEAD work the same way for their level. '
            'CMD and MAIN_ADMIN keep those people and every visible place.'
        ),
        parameters=[
            OpenApiParameter(
                name='designation',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                enum=[choice for choice, _label in Designation.choices],
                description=(
                    'Optional head filter. STATE_HEAD returns state heads and everything under their states. '
                    'The same applies to REGION_HEAD, DISTRICT_HEAD, AREA_HEAD, PROJECT_HEAD, CMD, and MAIN_ADMIN. '
                    'Leave it out to return everything this account can see.'
                ),
            ),
        ],
        responses={200: dict, 400: INVALID, 401: UNAUTHORIZED, 403: FORBIDDEN},
    )
    def get(self, request):
        actor = request.user
        designation = dashboard_designation(request.query_params.get('designation'))
        users = visible_queryset(
            actor,
            User.objects.select_related('state', 'region', 'district', 'area', 'project'),
        )
        states = visible_queryset(actor, State.objects.all())
        regions = visible_queryset(actor, Region.objects.select_related('state'))
        districts = visible_queryset(actor, District.objects.select_related('region__state'))
        areas = visible_queryset(actor, Area.objects.select_related('district__region__state'))
        projects = visible_queryset(actor, Project.objects.select_related('area__district__region__state'))
        sites = visible_queryset(
            actor,
            Site.objects.select_related('area__district__region__state', 'project', 'created_by'),
        )
        if designation:
            users, states, regions, districts, areas, projects, sites = apply_head_filter(
                designation,
                users,
                states,
                regions,
                districts,
                areas,
                projects,
                sites,
            )
        return Response(
            {
                'user': GetUserByIdSerializer(actor).data,
                'counts': {
                    'users': users.count(),
                    'states': states.count(),
                    'regions': regions.count(),
                    'districts': districts.count(),
                    'areas': areas.count(),
                    'projects': projects.count(),
                    'sites': sites.count(),
                },
                'users': GetUserSerializer(users, many=True).data,
                'states': GetStateSerializer(states, many=True).data,
                'regions': GetRegionSerializer(regions, many=True).data,
                'districts': GetDistrictSerializer(districts, many=True).data,
                'areas': GetAreaSerializer(areas, many=True).data,
                'projects': GetProjectSerializer(projects, many=True).data,
                'sites': GetSiteSerializer(sites, many=True).data,
            }
        )
