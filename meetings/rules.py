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

# Permission

rules.add_perm("meeting.read_dashboard", is_team_member)
rules.add_perm("meeting.write_dashboard", is_team_member)
