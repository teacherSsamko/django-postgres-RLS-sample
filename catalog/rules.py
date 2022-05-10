import rules


# Predicates

@rules.predicate
def is_staff(user):
    return user.is_superuser or user.is_staff

is_service_owner = rules.is_group_member("Thumb")

@rules.predicate
def is_team_member(user, team):
    return rules.is_group_member(team)
    # return team in user.groups

# team = "AWS"
# is_team_member = rules.is_group_member(team)

# Rules

# rules.add_rule("share_summary_link", is_team_member)
# rules.add_rule("delete_meeting", is_staff)

# Permission

rules.add_perm("meeting.read_dashboard", is_team_member)
rules.add_perm("meeting.write_dashboard", is_team_member)
