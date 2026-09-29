from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from configuration.openapi import PAGE_PARAM, PAGE_SIZE_PARAM, SEARCH_PARAM, UNAUTHORIZED
from setup.models import Project
from setup.serializers.project import ProjectForMapSerializer
from user.hierarchy import visible_queryset
from utils.pagination import Pagination


class ProjectForMapView(APIView):
    """Projects for the map, limited to the logged-in head's branch."""

    @extend_schema(
        tags=['Project'],
        operation_id='get_projects_for_map',
        summary='Projects for the map',
        description=(
            'Requires Authorization: Bearer <access_token>. '
            'Returns the projects this account is allowed to see. '
            'site_location is the polygon of the first site on that project. latitude and longitude are lists of numbers in the same order.'
        ),
        parameters=[SEARCH_PARAM, PAGE_PARAM, PAGE_SIZE_PARAM],
        responses={200: dict, 401: UNAUTHORIZED},
    )
    def get(self, request):
        projects = visible_queryset(
            request.user,
            Project.objects.select_related('area__district__region__state').prefetch_related('sites'),
        )
        search = (request.query_params.get('search') or '').strip()
        if search:
            projects = projects.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(phase__icontains=search)
                | Q(contractor__icontains=search)
                | Q(sites__address__icontains=search)
                | Q(sites__name__icontains=search)
            ).distinct()
        paginator = Pagination()
        page = paginator.paginate_queryset(projects, request, view=self)
        page_data = paginator.page_data(ProjectForMapSerializer(page, many=True).data)
        page_data['projects'] = page_data['results']
        return Response(
            {
                'success': True,
                'status': 200,
                'message': 'Projects retrieved successfully',
                'data': page_data,
            }
        )
