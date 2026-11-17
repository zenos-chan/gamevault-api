from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Achievement, Game, GameScore, GameSession, Player, PlayerAchievement

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(ModelAdmin):
    list_display = ('title', 'genre', 'developer', 'max_players', 'display_active', 'created_at')
    list_filter = ('genre', 'is_active')
    search_fields = ('title', 'developer', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_filter_submit = True

    @display(description="Active", boolean=True)
    def display_active(self, instance):
        return instance.is_active


@admin.register(Player)
class PlayerAdmin(ModelAdmin):
    list_display = ('gamer_tag', 'username', 'email', 'level', 'experience_points', 'display_status', 'created_at')
    list_filter = ('status', 'level')
    search_fields = ('gamer_tag', 'username', 'email')
    list_filter_submit = True

    @display(
        description="Status",
        label={
            "ONLINE": "success",
            "IN_GAME": "warning",
            "OFFLINE": "danger",
        },
    )
    def display_status(self, instance):
        return instance.status


@admin.register(GameScore)
class GameScoreAdmin(ModelAdmin):
    list_display = ('player', 'game', 'score', 'achieved_at')
    list_filter = ('game', 'achieved_at')
    search_fields = ('player__gamer_tag', 'game__title')
    list_filter_submit = True


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ('name', 'game', 'points', 'badge_icon', 'created_at')
    list_filter = ('game',)
    search_fields = ('name', 'description')
    list_filter_submit = True


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(ModelAdmin):
    list_display = ('player', 'achievement', 'unlocked_at')
    list_filter = ('achievement__game', 'unlocked_at')
    search_fields = ('player__gamer_tag', 'achievement__name')
    list_filter_submit = True


@admin.register(GameSession)
class GameSessionAdmin(ModelAdmin):
    list_display = ('room_code', 'game', 'display_status', 'winner', 'started_at', 'ended_at')
    list_filter = ('status', 'game')
    search_fields = ('room_code', 'game__title')
    filter_horizontal = ('players',)
    list_filter_submit = True

    @display(
        description="Session Status",
        label={
            "WAITING": "info",
            "IN_PROGRESS": "warning",
            "COMPLETED": "success",
            "CANCELLED": "danger",
        },
    )
    def display_status(self, instance):
        return instance.status
