from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AchievementViewSet,
    GameScoreViewSet,
    GameSessionViewSet,
    GameViewSet,
    PlayerAchievementViewSet,
    PlayerViewSet,
)

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'scores', GameScoreViewSet, basename='gamescore')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'player-achievements', PlayerAchievementViewSet, basename='playerachievement')
router.register(r'sessions', GameSessionViewSet, basename='gamesession')

urlpatterns = [
    path('', include(router.urls)),
]
