from django.contrib.auth.models import User
import rules

from .models import Meeting, Role

# Predicates

@rules.predicate
def is_staff(user):
    return user.is_superuser or user.is_staff

@rules.predicate
def is_team_member(user, team):
    return rules.is_group_member(team)

@rules.predicate
def has_view_meeting_permission(user: User, meeting: Meeting) -> bool:
    if user.is_superuser: return True
    if meeting.owner == user: return True

    def _check_shared_user(user: User, meeting: Meeting) -> bool:
        # TODO: Check user came via shared link
        # We need shared_link only in this case
        return True if meeting.shareduser_set.filter(user=user) else False

    if _check_shared_user(user, meeting): return True
    print("not shared user")


    def _find_all_groups_of(user: User) -> set:
        return set(user.groups.values_list('name', flat=True))

    def _check_in_same_group(a: User, b: User) -> bool:
        same_groups = _find_all_groups_of(a).intersection(_find_all_groups_of(b))
        return True if same_groups else False

    if _check_in_same_group(user, meeting.owner): return True

    return False

@rules.predicate
def is_admin(user, team):
    if not rules.is_group_member(team): False
    user_role = Role.objects.get(user=user, team=team).user_role
    if user_role == Role.Roles.ADMIN.value: return True

    return False


# Permission

rules.add_perm("meetings.read_meeting_detail", has_view_meeting_permission)
rules.add_perm("meetings.write_meeting_detail", is_admin)

rules.add_perm("meetings.read_dashboard_detail", is_team_member)
rules.add_perm("meetings.read_dashboard_list", is_team_member)

# rules.add_perm("meetings.write_via_link")