from django.db.models.signals import post_save
from django.db import connection, transaction
from django.dispatch import receiver
from django.contrib.auth.models import Group, User

from .models import Meeting, Dashboard, MeetingDetail

@receiver(post_save, sender=Meeting)
def create_post_meeting_objects(sender, instance: Meeting, created, **kwargs):
    if created:
        with transaction.atomic():
            data = f"{instance.team}'s meeting script"
            dashboard_for_owner = Dashboard(
                meeting = instance,
                contents = data,
                owner = instance.owner
            )
            dashboard_for_owner.save()
            detail = MeetingDetail(
                meeting = instance,
                data = data
            )
            detail.save()

@receiver(post_save, sender=Group)
def create_team_role(sender, instance: Group, created, **kwargs):
    if created:
        with connection.cursor() as db:
            role = instance.name
            db.execute(f"CREATE ROLE {role}")
            # put below stmt into WHERE clause for selecting multiple app
            # select table_name FROM information_schema.tables WHERE table_name SIMILAR TO 'meetings\_%|catalog\_%';
            GRANT_SELECT_STMT = f"""DO
$$
DECLARE
    t record;
BEGIN
    FOR t IN 
    SELECT table_name
    FROM information_schema.tables
    WHERE table_name LIKE 'meetings\_%'
    LOOP
        EXECUTE format('GRANT select ON TABLE %I TO {role}', t.table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
"""
            db.execute(GRANT_SELECT_STMT)


@receiver(post_save, sender=User)
def create_db_user(sender, instance: User, created, **kwargs):
    is_superuser = instance.is_superuser
    is_staff = instance.is_staff
    user_id = instance.pk
    teams = instance.groups.values_list('name', flat=True)
    with connection.cursor() as cursor:
        if created:
            create_role_stmt = f'CREATE ROLE "{user_id}"'
            create_role_stmt += " WITH SUPERUSER" if is_superuser else ""
            cursor.execute(create_role_stmt)
        elif is_superuser or is_staff:
            alter_role_stmt = f'ALTER ROLE "{user_id}" WITH SUPERUSER'
            cursor.execute(alter_role_stmt)
        # update user's team
        for team in teams:
            # is it possible to be in multiple teams?
            cursor.execute(f'GRANT {team} TO "{user_id}"')
