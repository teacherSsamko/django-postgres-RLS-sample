from django.db import connection

class RlsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user_id = request.user.id
        if user_id:
            team = request.user.groups.first().name.lower()
        # TODO: according to what ROLE user need, SET ROLE team or user
        with connection.cursor() as cursor:
            if user_id and "accounts" not in request.path and "admin" not in request.path:
                if team:
                    cursor.execute(f'SET ROLE "{team}"')
                else:
                    cursor.execute(f'SET ROLE "{user_id}"')
            else:
                cursor.execute(f'SET ROLE "postgres"')
        

        response = self.get_response(request)
        return response