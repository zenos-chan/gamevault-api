from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({
        'name': 'Game Platform REST API',
        'version': '1.0.0',
        'database': 'SQLite',
        'endpoints': {
            'games': '/api/games/',
            'players': '/api/players/',
            'scores': '/api/scores/',
            'achievements': '/api/achievements/',
            'player_achievements': '/api/player-achievements/',
            'sessions': '/api/sessions/',
            'admin': '/admin/',
        },
        'quick_actions': {
            'game_leaderboard': '/api/games/{id}/leaderboard/',
            'game_achievements': '/api/games/{id}/achievements/',
            'player_profile': '/api/players/{id}/profile/',
            'update_player_status': 'POST /api/players/{id}/status/ (body: {"status": "ONLINE|OFFLINE|IN_GAME"})',
            'join_session': 'POST /api/sessions/{id}/join/ (body: {"player_id": <id>})',
            'start_session': 'POST /api/sessions/{id}/start/',
            'finish_session': 'POST /api/sessions/{id}/finish/ (body: {"winner_id": <id>})',
        }
    })


urlpatterns = [
    path('', api_root, name='project-home'),
    path('admin/', admin.site.urls),
    path('api/', include('games.urls')),
]
