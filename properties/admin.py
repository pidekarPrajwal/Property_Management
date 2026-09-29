from django.contrib import admin

from properties.models import Property, PropertySyncLog


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'property_id',
        'address',
        'latitude',
        'longitude',
        'area_sqft',
        'market_rate',
        'current_market_rate',
        'owner_name',
        'status',
    )
    search_fields = ('property_id', 'address', 'owner_name')


@admin.register(PropertySyncLog)
class PropertySyncLogAdmin(admin.ModelAdmin):
    list_display = ('filename', 'synced_at', 'inserted', 'updated', 'skipped', 'failed')
    readonly_fields = ('filename', 'synced_at', 'inserted', 'updated', 'skipped', 'failed')
