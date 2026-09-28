from django.contrib import admin

from setup.models import Area, District, Project, Region, Site, State

admin.site.site_header = 'Property Management'
admin.site.site_title = 'Property Management'
admin.site.index_title = 'Setup'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'state', 'created_at')
    list_filter = ('state',)
    search_fields = ('name', 'code')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'created_at')
    list_filter = ('region__state', 'region')
    search_fields = ('name', 'code')


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district', 'created_at')
    list_filter = ('district__region__state',)
    search_fields = ('name', 'code')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area', 'created_at')
    list_filter = ('area__district__region__state',)
    search_fields = ('name', 'code')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'latitude', 'longitude', 'area', 'project', 'is_active', 'created_by')
    list_filter = ('is_active', 'area')
    search_fields = ('name', 'code', 'address')
