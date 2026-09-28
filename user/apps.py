import sys

from django.apps import AppConfig
from django.db.utils import IntegrityError, OperationalError, ProgrammingError

from user.designations import Designation

STATIC_USERNAME = 'admin'
STATIC_PASSWORD = '123456'


def ensure_static_admin():
    """Keep one fixed CMD account so login works without createsuperuser."""
    from user.models import User

    user = User.objects.filter(username=STATIC_USERNAME).first()
    if user is None:
        user = User(
            username=STATIC_USERNAME,
            email='admin@example.com',
            mobile_number='1234567890',
            first_name='Admin',
            last_name='User',
            designation=Designation.CMD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
    user.set_password(STATIC_PASSWORD)
    user.is_active = True
    user.save()


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        if any(command in sys.argv for command in ('makemigrations', 'migrate', 'collectstatic')):
            return
        try:
            ensure_static_admin()
        except (OperationalError, ProgrammingError, IntegrityError):
            return
