from django.db import connection

class RlsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user_id = request.user.id
        with connection.cursor() as cursor:
            if user_id:
                cursor.execute(f'SET ROLE "{user_id}"')
            else:
                cursor.execute(f'SET ROLE "postgres"')
        

        response = self.get_response(request)
        return response