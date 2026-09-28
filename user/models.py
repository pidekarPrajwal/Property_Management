from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.core.validators import RegexValidator
from django.db import models

from user.designations import Designation, validate_location_assignment

mobile_number_validator = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message='Enter a mobile number with 10 to 15 digits. A leading + is allowed.',
)


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # The first account created from the command line is the top of the hierarchy.
        extra_fields.setdefault('designation', Designation.CMD)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(
        max_length=16,
        unique=True,
        validators=[mobile_number_validator],
    )
    designation = models.CharField(max_length=20, choices=Designation.choices)
    state = models.ForeignKey(
        'setup.State',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    region = models.ForeignKey(
        'setup.Region',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    district = models.ForeignKey(
        'setup.District',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    area = models.ForeignKey(
        'setup.Area',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    project = models.ForeignKey(
        'setup.Project',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = ['email', 'mobile_number', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.username} ({self.get_designation_display()})'

    def clean(self):
        super().clean()
        validate_location_assignment(
            self.designation,
            self.state,
            self.region,
            self.district,
            self.area,
            self.project,
        )

    def save(self, *args, **kwargs):
        # Login only updates last_login. Skip the full hierarchy check on that write.
        update_fields = kwargs.get('update_fields')
        if update_fields is None or set(update_fields) != {'last_login'}:
            self.full_clean()
        return super().save(*args, **kwargs)
