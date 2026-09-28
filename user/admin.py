from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from user.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('id',)
    list_display = ('username', 'email', 'mobile_number', 'designation', 'state', 'is_active')
    list_filter = ('designation', 'is_active', 'state')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile_number')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'Hierarchy',
            {
                'fields': (
                    'mobile_number',
                    'designation',
                    'state',
                    'region',
                    'district',
                    'area',
                    'project',
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            'Hierarchy',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'mobile_number',
                    'designation',
                    'state',
                    'region',
                    'district',
                    'area',
                    'project',
                )
            },
        ),
    )
