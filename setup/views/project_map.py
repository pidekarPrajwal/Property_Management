from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from configuration.openapi import UNAUTHORIZED
from setup.models import Project
from setup.serializers.project import ProjectForMapSerializer
from user.hierarchy import visible_queryset


class ProjectForMapView(APIView):
    """Projects for the map, limited to the logged-in head's branch."""

    @extend_schema(
        tags=['Project'],
        operation_id='get_projects_for_map',
        summary='Projects for the map',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Returns the projects this account is allowed to see. '
            'site_location is the latitude and longitude of the first site on that project.'
        ),
        responses={200: dict, 401: UNAUTHORIZED},
    )
    def get(self, request):
        projects = visible_queryset(
            request.user,
            Project.objects.select_related('area__district__region__state').prefetch_related('sites'),
        )
        return Response(
            {
                'success': True,
                'status': 200,
                'message': 'Projects retrieved successfully',
                'data': {
                    'projects': ProjectForMapSerializer(projects, many=True).data,
                },
            }
        )
