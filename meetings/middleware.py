from django.db import connection
from django.conf import settings


class SharingAsMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        with connection.cursor() as db:
            db.execute(f"SET ROLE {settings.DATABASES['default']['USER']}")
            print("set DB role back")

        return self.get_response(request)