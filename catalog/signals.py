from .models import Newuser
from django.db.models.signals import post_save
from django.db import connection

def create_db_user(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE ROLE "{user_id}"')
            cursor.execute(f'GRANT author TO "{user_id}')

post_save.connect(create_db_user, sender=Newuser)