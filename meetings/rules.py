from django.contrib.auth.models import User, Group
import rules

from .models import Meeting

# Predicates

@rules.predicate
def is_staff(user):
    return user.is_superuser or user.is_staff

@rules.predicate
def is_team_member(user, team):
    return rules.is_group_member(team)

@rules.predicate
def has_view_permission(user: User, meeting: Meeting) -> bool:
    if user.is_superuser: return True
    print("not superuser")
    if meeting.owner == user: return True
    print("not meeting owner")

    def _check_shared_user(user: User, meeting: Meeting) -> bool:
        return True if meeting.shareduser_set.filter(user=user) else False

    def _find_all_groups_of(user: User) -> set:
        return set(user.groups.values_list('name', flat=True))

    def _check_in_same_group(a: User, b: User) -> bool:
        same_groups = _find_all_groups_of(a).intersection(_find_all_groups_of(b))
        return True if same_groups else False

    if _check_shared_user(user, meeting): return True
    print("not shared user")
    if _check_in_same_group(user, meeting.owner): return True

    return False


# Permission

rules.add_perm("meetings.read_meeting_detail", rules.is_authenticated and has_view_permission)

rules.add_perm("meetings.read_dashboard", is_team_member)
rules.add_perm("meetings.write_dashboard", is_team_member)
rules.add_perm("meetings.read_dashboard_detail", is_team_member)
rules.add_perm("meetings.read_dashboard_list", is_team_member)
