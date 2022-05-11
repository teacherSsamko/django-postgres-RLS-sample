# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.db import connection
# from django.dispatch import receiver

# @receiver(post_save, sender=User)
# def create_db_user(sender, instance, created, **kwargs):
#     is_superuser = instance.is_superuser
#     is_staff = instance.is_staff
#     user_id = instance.id
#     if created:
#         with connection.cursor() as cursor:
#             create_role_stmt = f'CREATE ROLE "{user_id}"'
#             create_role_stmt += " WITH SUPERUSER" if is_superuser else ""
#             cursor.execute(create_role_stmt)
#             cursor.execute(f'GRANT author TO "{user_id}"')
#     elif is_superuser or is_staff:
#         alter_role_stmt = f'ALTER ROLE "{user_id}" WITH SUPERUSER'
#         with connection.cursor() as cursor:
#             cursor.execute(alter_role_stmt)
