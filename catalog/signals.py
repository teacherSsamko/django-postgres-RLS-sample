from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_db_user(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE ROLE "{user_id}"')
            cursor.execute(f'GRANT author TO "{user_id}"')
