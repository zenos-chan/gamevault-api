from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from rest_framework.authtoken.admin import TokenAdmin as BaseTokenAdmin
from rest_framework.authtoken.models import TokenProxy
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import ApiUserProfile, Game

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


try:
    admin.site.unregister(TokenProxy)
except admin.sites.NotRegistered:
    pass


@admin.register(TokenProxy)
class TokenAdmin(BaseTokenAdmin, ModelAdmin):
    list_display = ('key', 'user', 'created')
    search_fields = ('user__username', 'user__email', 'key')


@admin.register(Game)
class GameAdmin(ModelAdmin):
    list_display = ('title', 'genre', 'developer', 'rating', 'display_active', 'release_date', 'created_at')
    list_filter = ('genre', 'is_active')
    search_fields = ('title', 'developer', 'publisher', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_filter_submit = True

    @display(description="Active", boolean=True)
    def display_active(self, instance):
        return instance.is_active


@admin.register(ApiUserProfile)
class ApiUserProfileAdmin(ModelAdmin):
    list_display = ('user', 'display_tier', 'rate_limit_per_minute', 'display_active', 'created_at')
    list_filter = ('tier', 'is_active')
    search_fields = ('user__username', 'user__email')
    list_filter_submit = True

    @display(
        description="Subscription Tier",
        label={
            "FREE": "info",
            "PRO": "warning",
            "ENTERPRISE": "success",
        },
    )
    def display_tier(self, instance):
        return instance.tier

    @display(description="Active", boolean=True)
    def display_active(self, instance):
        return instance.is_active
