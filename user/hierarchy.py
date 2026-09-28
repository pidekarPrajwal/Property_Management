"""Who can see and change records.

CMD and Main Admin can see the whole organisation.
Everyone else can see their own place, the single path above them, and every
record under them. They cannot see a neighbouring branch.

Changing a record is stricter than viewing it. A person can change their own
place and everything under it. They cannot change the levels above them.
Creating a child (for example a Region under a State) is allowed only when the
person is allowed to change that parent.

Site creation is a separate rule: only an Area Head can create a site, and only
inside their own area.
"""

from django.db.models import Q

from setup.models import Area, District, Project, Region, Site, State
from user.designations import DESIGNATION_RANK, Designation, GLOBAL_DESIGNATIONS
from user.models import User


def is_global_access(user):
    return getattr(user, 'designation', None) in GLOBAL_DESIGNATIONS


def can_manage_designation(actor, designation):
    """A person may manage users strictly below their own designation.

    CMD can manage every designation, including another CMD.
    """
    if actor.designation == Designation.CMD:
        return True
    if designation not in DESIGNATION_RANK:
        return False
    return DESIGNATION_RANK[designation] > DESIGNATION_RANK[actor.designation]


def outside_scope_message(actor, state, region, district, area, project):
    """Return a message when the place is outside the actor's branch."""
    if is_global_access(actor):
        return None

    if actor.designation == Designation.STATE_HEAD:
        if state is None or state.id != actor.state_id:
            return 'You can only manage users inside your state.'
        return None
    if actor.designation == Designation.REGION_HEAD:
        if region is None or region.id != actor.region_id:
            return 'You can only manage users inside your region.'
        return None
    if actor.designation == Designation.DISTRICT_HEAD:
        if district is None or district.id != actor.district_id:
            return 'You can only manage users inside your district.'
        return None
    if actor.designation == Designation.AREA_HEAD:
        if area is None or area.id != actor.area_id:
            return 'You can only manage users inside your area.'
        return None
    if actor.designation == Designation.PROJECT_HEAD:
        if project is None or project.id != actor.project_id:
            return 'You can only manage users inside your project.'
        return None
    return 'You are not allowed to manage users.'


def visible_queryset(user, queryset):
    model = queryset.model
    if model is User:
        return _filter_users(user, queryset)
    if model is State:
        return _filter_states(user, queryset)
    if model is Region:
        return _filter_regions(user, queryset)
    if model is District:
        return _filter_districts(user, queryset)
    if model is Area:
        return _filter_areas(user, queryset)
    if model is Project:
        return _filter_projects(user, queryset)
    if model is Site:
        return _filter_sites(user, queryset)
    return queryset.none()


def _lookup(user):
    return {
        Designation.STATE_HEAD: 'state_id',
        Designation.REGION_HEAD: 'region_id',
        Designation.DISTRICT_HEAD: 'district_id',
        Designation.AREA_HEAD: 'area_id',
        Designation.PROJECT_HEAD: 'project_id',
    }.get(user.designation)


def _filter_users(user, queryset):
    if is_global_access(user):
        return queryset
    lookup = _lookup(user)
    value = getattr(user, lookup, None) if lookup else None
    if not lookup or not value:
        return queryset.filter(pk=user.pk)
    return queryset.filter(Q(**{lookup: value}) | Q(pk=user.pk))


def _filter_states(user, queryset):
    if is_global_access(user):
        return queryset
    if not user.state_id:
        return queryset.none()
    return queryset.filter(id=user.state_id)


def _filter_regions(user, queryset):
    if is_global_access(user):
        return queryset
    if user.designation == Designation.STATE_HEAD:
        return queryset.filter(state_id=user.state_id)
    if user.region_id:
        return queryset.filter(id=user.region_id)
    return queryset.none()


def _filter_districts(user, queryset):
    if is_global_access(user):
        return queryset
    if user.designation == Designation.STATE_HEAD:
        return queryset.filter(region__state_id=user.state_id)
    if user.designation == Designation.REGION_HEAD:
        return queryset.filter(region_id=user.region_id)
    if user.district_id:
        return queryset.filter(id=user.district_id)
    return queryset.none()


def _filter_areas(user, queryset):
    if is_global_access(user):
        return queryset
    if user.designation == Designation.STATE_HEAD:
        return queryset.filter(district__region__state_id=user.state_id)
    if user.designation == Designation.REGION_HEAD:
        return queryset.filter(district__region_id=user.region_id)
    if user.designation == Designation.DISTRICT_HEAD:
        return queryset.filter(district_id=user.district_id)
    if user.area_id:
        return queryset.filter(id=user.area_id)
    return queryset.none()


def _filter_projects(user, queryset):
    if is_global_access(user):
        return queryset
    if user.designation == Designation.STATE_HEAD:
        return queryset.filter(area__district__region__state_id=user.state_id)
    if user.designation == Designation.REGION_HEAD:
        return queryset.filter(area__district__region_id=user.region_id)
    if user.designation == Designation.DISTRICT_HEAD:
        return queryset.filter(area__district_id=user.district_id)
    if user.designation == Designation.AREA_HEAD:
        return queryset.filter(area_id=user.area_id)
    if user.project_id:
        return queryset.filter(id=user.project_id)
    return queryset.none()


def _filter_sites(user, queryset):
    if is_global_access(user):
        return queryset
    if user.designation == Designation.STATE_HEAD:
        return queryset.filter(area__district__region__state_id=user.state_id)
    if user.designation == Designation.REGION_HEAD:
        return queryset.filter(area__district__region_id=user.region_id)
    if user.designation == Designation.DISTRICT_HEAD:
        return queryset.filter(area__district_id=user.district_id)
    if user.designation == Designation.AREA_HEAD:
        return queryset.filter(area_id=user.area_id)
    if user.project_id:
        return queryset.filter(project_id=user.project_id)
    return queryset.none()


def can_modify_state(user, state):
    if is_global_access(user):
        return True
    return user.designation == Designation.STATE_HEAD and state is not None and user.state_id == state.id


def can_modify_region(user, region):
    if is_global_access(user):
        return True
    if region is None:
        return False
    if user.designation == Designation.STATE_HEAD:
        return user.state_id == region.state_id
    return user.designation == Designation.REGION_HEAD and user.region_id == region.id


def can_modify_district(user, district):
    if is_global_access(user):
        return True
    if district is None:
        return False
    if user.designation == Designation.STATE_HEAD:
        return user.state_id == district.region.state_id
    if user.designation == Designation.REGION_HEAD:
        return user.region_id == district.region_id
    return user.designation == Designation.DISTRICT_HEAD and user.district_id == district.id


def can_modify_area(user, area):
    if is_global_access(user):
        return True
    if area is None:
        return False
    if user.designation == Designation.STATE_HEAD:
        return user.state_id == area.district.region.state_id
    if user.designation == Designation.REGION_HEAD:
        return user.region_id == area.district.region_id
    if user.designation == Designation.DISTRICT_HEAD:
        return user.district_id == area.district_id
    return user.designation == Designation.AREA_HEAD and user.area_id == area.id


def can_modify_project(user, project):
    if is_global_access(user):
        return True
    if project is None:
        return False
    if user.designation == Designation.STATE_HEAD:
        return user.state_id == project.area.district.region.state_id
    if user.designation == Designation.REGION_HEAD:
        return user.region_id == project.area.district.region_id
    if user.designation == Designation.DISTRICT_HEAD:
        return user.district_id == project.area.district_id
    if user.designation == Designation.AREA_HEAD:
        return user.area_id == project.area_id
    return user.designation == Designation.PROJECT_HEAD and user.project_id == project.id


def can_modify_site(user, area, project):
    """View, update and delete follow the person's branch. Creation does not."""
    if is_global_access(user):
        return True
    if area is None or project is None:
        return False
    if user.designation == Designation.STATE_HEAD:
        return user.state_id == area.district.region.state_id
    if user.designation == Designation.REGION_HEAD:
        return user.region_id == area.district.region_id
    if user.designation == Designation.DISTRICT_HEAD:
        return user.district_id == area.district_id
    if user.designation == Designation.AREA_HEAD:
        return user.area_id == area.id
    if user.designation == Designation.PROJECT_HEAD:
        return user.project_id == project.id
    return False


def can_create_site(user, area, project):
    """Only the Area Head of this area may add a site, and only for a project in that area."""
    if getattr(user, 'designation', None) != Designation.AREA_HEAD:
        return False
    if area is None or project is None or user.area_id != area.id:
        return False
    return project.area_id == area.id
