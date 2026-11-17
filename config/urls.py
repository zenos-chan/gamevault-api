from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({
        'name': 'Game Database & Details REST API',
        'version': '2.0.0',
        'database': 'SQLite',
        'authentication': {
            'header': 'Authorization: Token <your_access_token>',
            'sign_up': 'POST /api/auth/register/',
            'get_token': 'POST /api/auth/token/ or POST /api/auth/login/',
            'my_profile_and_limits': 'GET /api/auth/me/',
        },
        'rate_limits': {
            'default_free_tier': '60 calls/minute',
            'pro_tier': '300 calls/minute',
            'enterprise_tier': '1200 calls/minute',
        },
        'endpoints': {
            'list_games': 'GET /api/games/ (optional filters: ?name=..., ?genre=..., ?platform=...)',
            'game_details_by_id': 'GET /api/games/{id}/',
            'game_details_by_name_or_slug': 'GET /api/games/{name_or_slug}/',
            'game_by_name_query': 'GET /api/games/by-name/?name={title}',
            'admin_dashboard': '/admin/',
        },
    })


urlpatterns = [
    path('', api_root, name='project-home'),
    path('admin/', admin.site.urls),
    path('api/', include('games.urls')),
]
