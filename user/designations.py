"""Designation rules shared by the user model and the API."""

from django.core.exceptions import ValidationError
from django.db import models


class Designation(models.TextChoices):
    CMD = 'CMD', 'CMD'
    MAIN_ADMIN = 'MAIN_ADMIN', 'Main Admin'
    STATE_HEAD = 'STATE_HEAD', 'State Head'
    REGION_HEAD = 'REGION_HEAD', 'Region Head'
    DISTRICT_HEAD = 'DISTRICT_HEAD', 'District Head'
    AREA_HEAD = 'AREA_HEAD', 'Area Head'
    PROJECT_HEAD = 'PROJECT_HEAD', 'Project Head'


# Lower number means a higher position in the organisation.
DESIGNATION_RANK = {
    Designation.CMD: 1,
    Designation.MAIN_ADMIN: 2,
    Designation.STATE_HEAD: 3,
    Designation.REGION_HEAD: 4,
    Designation.DISTRICT_HEAD: 5,
    Designation.AREA_HEAD: 6,
    Designation.PROJECT_HEAD: 7,
}

DESIGNATION_LABEL = {
    Designation.CMD: 'CMD',
    Designation.MAIN_ADMIN: 'Main Admin',
    Designation.STATE_HEAD: 'State Head',
    Designation.REGION_HEAD: 'Region Head',
    Designation.DISTRICT_HEAD: 'District Head',
    Designation.AREA_HEAD: 'Area Head',
    Designation.PROJECT_HEAD: 'Project Head',
}

# A user may only keep the location fields that match their designation.
REQUIRED_LOCATION_FIELDS = {
    Designation.CMD: [],
    Designation.MAIN_ADMIN: [],
    Designation.STATE_HEAD: ['state'],
    Designation.REGION_HEAD: ['state', 'region'],
    Designation.DISTRICT_HEAD: ['state', 'region', 'district'],
    Designation.AREA_HEAD: ['state', 'region', 'district', 'area'],
    Designation.PROJECT_HEAD: ['state', 'region', 'district', 'area', 'project'],
}

LOCATION_FIELDS = ['state', 'region', 'district', 'area', 'project']

GLOBAL_DESIGNATIONS = {Designation.CMD, Designation.MAIN_ADMIN}


def validate_location_assignment(designation, state, region, district, area, project):
    """Reject a user whose location fields do not match the organisation tree.

    CMD and Main Admin are not tied to a place. Every other designation must
    be linked to its own level and to every level above it, and must not be
    linked to a level below it. Each child must belong to the selected parent.
    """
    if designation not in REQUIRED_LOCATION_FIELDS:
        raise ValidationError({'designation': 'Select a valid designation.'})

    values = {
        'state': state,
        'region': region,
        'district': district,
        'area': area,
        'project': project,
    }
    required = REQUIRED_LOCATION_FIELDS[designation]
    label = DESIGNATION_LABEL[designation]
    errors = {}

    for field in LOCATION_FIELDS:
        if field in required and values[field] is None:
            errors[field] = f'A {label} must be linked to a {field}.'
        elif field not in required and values[field] is not None:
            errors[field] = (
                f'A {label} cannot be linked to a {field}. Leave {field} empty.'
            )

    chain_ready = set(required)
    if (
        'region' in chain_ready
        and region is not None
        and state is not None
        and region.state_id != state.id
    ):
        errors['region'] = 'The selected region does not belong to the selected state.'
    if (
        'district' in chain_ready
        and district is not None
        and region is not None
        and district.region_id != region.id
    ):
        errors['district'] = 'The selected district does not belong to the selected region.'
    elif (
        'district' in chain_ready
        and district is not None
        and state is not None
        and district.region.state_id != state.id
    ):
        errors['district'] = 'The selected district does not belong to the selected state.'
    if (
        'area' in chain_ready
        and area is not None
        and district is not None
        and area.district_id != district.id
    ):
        errors['area'] = 'The selected area does not belong to the selected district.'
    elif (
        'area' in chain_ready
        and area is not None
        and region is not None
        and area.district.region_id != region.id
    ):
        errors['area'] = 'The selected area does not belong to the selected region.'
    if (
        'project' in chain_ready
        and project is not None
        and area is not None
        and project.area_id != area.id
    ):
        errors['project'] = 'The selected project does not belong to the selected area.'
    elif (
        'project' in chain_ready
        and project is not None
        and district is not None
        and project.area.district_id != district.id
    ):
        errors['project'] = 'The selected project does not belong to the selected district.'

    if errors:
        raise ValidationError(errors)
