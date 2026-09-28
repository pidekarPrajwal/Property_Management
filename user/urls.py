from django.urls import path

from user.views.auth import LoginView, LogoutView, RefreshView
from user.views.user import UserViewSet

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh/', RefreshView.as_view(), name='auth-refresh'),
    path('add-user/', UserViewSet.as_view({'post': 'create_user'}), name='add-user'),
    path('get-users/', UserViewSet.as_view({'get': 'get_all_user'}), name='get-users'),
    path('get-user-by-id/', UserViewSet.as_view({'get': 'get_user_by_id'}), name='get-user-by-id'),
    path(
        'update-user/',
        UserViewSet.as_view({'put': 'update_user', 'patch': 'update_user'}),
        name='update-user',
    ),
    path('delete-user/', UserViewSet.as_view({'delete': 'delete_user'}), name='delete-user'),
]
