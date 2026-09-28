from django.urls import path

from setup.views.area import AreaViewSet
from setup.views.dashboard import DashboardView
from setup.views.district import DistrictViewSet
from setup.views.project import ProjectViewSet
from setup.views.project_map import ProjectForMapView
from setup.views.region import RegionViewSet
from setup.views.site import SiteViewSet
from setup.views.state import StateViewSet

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('add-state/', StateViewSet.as_view({'post': 'create_state'}), name='add-state'),
    path('get-states/', StateViewSet.as_view({'get': 'get_all_state'}), name='get-states'),
    path('get-state-by-id/', StateViewSet.as_view({'get': 'get_state_by_id'}), name='get-state-by-id'),
    path(
        'update-state/',
        StateViewSet.as_view({'put': 'update_state', 'patch': 'update_state'}),
        name='update-state',
    ),
    path('delete-state/', StateViewSet.as_view({'delete': 'delete_state'}), name='delete-state'),
    path('add-region/', RegionViewSet.as_view({'post': 'create_region'}), name='add-region'),
    path('get-regions/', RegionViewSet.as_view({'get': 'get_all_region'}), name='get-regions'),
    path('get-region-by-id/', RegionViewSet.as_view({'get': 'get_region_by_id'}), name='get-region-by-id'),
    path(
        'update-region/',
        RegionViewSet.as_view({'put': 'update_region', 'patch': 'update_region'}),
        name='update-region',
    ),
    path('delete-region/', RegionViewSet.as_view({'delete': 'delete_region'}), name='delete-region'),
    path('add-district/', DistrictViewSet.as_view({'post': 'create_district'}), name='add-district'),
    path('get-districts/', DistrictViewSet.as_view({'get': 'get_all_district'}), name='get-districts'),
    path(
        'get-district-by-id/',
        DistrictViewSet.as_view({'get': 'get_district_by_id'}),
        name='get-district-by-id',
    ),
    path(
        'update-district/',
        DistrictViewSet.as_view({'put': 'update_district', 'patch': 'update_district'}),
        name='update-district',
    ),
    path('delete-district/', DistrictViewSet.as_view({'delete': 'delete_district'}), name='delete-district'),
    path('add-area/', AreaViewSet.as_view({'post': 'create_area'}), name='add-area'),
    path('get-areas/', AreaViewSet.as_view({'get': 'get_all_area'}), name='get-areas'),
    path('get-area-by-id/', AreaViewSet.as_view({'get': 'get_area_by_id'}), name='get-area-by-id'),
    path(
        'update-area/',
        AreaViewSet.as_view({'put': 'update_area', 'patch': 'update_area'}),
        name='update-area',
    ),
    path('delete-area/', AreaViewSet.as_view({'delete': 'delete_area'}), name='delete-area'),
    path('add-project/', ProjectViewSet.as_view({'post': 'create_project'}), name='add-project'),
    path('get-projects/', ProjectViewSet.as_view({'get': 'get_all_project'}), name='get-projects'),
    path('project-for-map/', ProjectForMapView.as_view(), name='project-for-map'),
    path('get-project-by-id/', ProjectViewSet.as_view({'get': 'get_project_by_id'}), name='get-project-by-id'),
    path(
        'update-project/',
        ProjectViewSet.as_view({'put': 'update_project', 'patch': 'update_project'}),
        name='update-project',
    ),
    path('delete-project/', ProjectViewSet.as_view({'delete': 'delete_project'}), name='delete-project'),
    path('add-site/', SiteViewSet.as_view({'post': 'create_site'}), name='add-site'),
    path('get-sites/', SiteViewSet.as_view({'get': 'get_all_site'}), name='get-sites'),
    path('get-site-by-id/', SiteViewSet.as_view({'get': 'get_site_by_id'}), name='get-site-by-id'),
    path(
        'update-site/',
        SiteViewSet.as_view({'put': 'update_site', 'patch': 'update_site'}),
        name='update-site',
    ),
    path('delete-site/', SiteViewSet.as_view({'delete': 'delete_site'}), name='delete-site'),
]
