from django.contrib import admin
from .models import Game, Player, GameScore, Achievement, PlayerAchievement, GameSession


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'developer', 'max_players', 'is_active', 'created_at')
    list_filter = ('genre', 'is_active')
    search_fields = ('title', 'developer', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('gamer_tag', 'username', 'email', 'level', 'experience_points', 'status', 'created_at')
    list_filter = ('status', 'level')
    search_fields = ('gamer_tag', 'username', 'email')


@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'score', 'achieved_at')
    list_filter = ('game', 'achieved_at')
    search_fields = ('player__gamer_tag', 'game__title')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'points', 'badge_icon', 'created_at')
    list_filter = ('game',)
    search_fields = ('name', 'description')


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ('player', 'achievement', 'unlocked_at')
    list_filter = ('achievement__game', 'unlocked_at')
    search_fields = ('player__gamer_tag', 'achievement__name')


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'game', 'status', 'winner', 'started_at', 'ended_at')
    list_filter = ('status', 'game')
    search_fields = ('room_code', 'game__title')
    filter_horizontal = ('players',)
