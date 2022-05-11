import rules


# Predicates

@rules.predicate
def is_staff(user):
    return user.is_superuser or user.is_staff

is_service_owner = rules.is_group_member("Thumb")

@rules.predicate
def is_team_member(user, dashboard):
    if dashboard.meeting.team:
        return dashboard.meeting.team.name in user.groups.values_list('name', flat=True)
    return False

# team = "AWS"
# is_team_member = rules.is_group_member(team)

# Rules

# rules.add_rule("share_summary_link", is_team_member)
# rules.add_rule("delete_meeting", is_staff)

# Permission

rules.add_perm("meetings.read_dashboard", is_team_member | is_service_owner)
# rules.add_perm("meetings.create_dashboard", is_team_member)
