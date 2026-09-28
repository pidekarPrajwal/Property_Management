from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from configuration.openapi import UNAUTHORIZED
from setup.models import Area, District, Project, Region, Site, State
from setup.serializers.area import GetAreaSerializer
from setup.serializers.district import GetDistrictSerializer
from setup.serializers.project import GetProjectSerializer
from setup.serializers.region import GetRegionSerializer
from setup.serializers.site import GetSiteSerializer
from setup.serializers.state import GetStateSerializer
from user.hierarchy import visible_queryset
from user.models import User
from user.serializers.user import GetUserByIdSerializer, GetUserSerializer


class DashboardView(APIView):
    """One screen of data for the logged-in head, limited to their branch."""

    @extend_schema(
        tags=['Dashboard'],
        operation_id='get_dashboard',
        summary='Dashboard for the logged-in head',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Returns only the people and places this account is allowed to see. '
            'A State Head sees their state and everything under it. '
            'A Project Head sees only their project. '
            'CMD and Main Admin see the whole organisation.'
        ),
        responses={200: dict, 401: UNAUTHORIZED},
    )
    def get(self, request):
        actor = request.user
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
