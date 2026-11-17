from functools import update_wrapper
from django.contrib import admin
from django.contrib.contenttypes import views as contenttype_views
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView
from unfold.sites import UnfoldAdminSite


class CleanUnfoldAdminSite(UnfoldAdminSite):
    """
    Enhanced Unfold Admin Site providing clean, elegant, SEO-friendly model URLs
    (e.g., /admin/games/ instead of /admin/games/game/).
    Also preserves full backward-compatibility with 301 permanent redirects.
    """

    MODEL_ROUTES = {
        'games.game': 'games',
        'games.player': 'players',
        'games.gamescore': 'leaderboards',
        'games.achievement': 'achievements',
        'games.playerachievement': 'badges',
        'games.gamesession': 'sessions',
        'auth.user': 'users',
        'auth.group': 'groups',
    }

    def get_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            wrapper.login_url = reverse_lazy("admin:login", current_app=self.name)
            return update_wrapper(wrapper, view)

        # 1. Base Admin & Unfold URLs
        urlpatterns = [
            path("search/", self.admin_view(self.search), name="search"),
            path("", wrap(self.index), name="index"),
            path("login/", self.login, name="login"),
            path("logout/", wrap(self.logout), name="logout"),
            path(
                "password_change/",
                wrap(self.password_change, cacheable=True),
                name="password_change",
            ),
            path(
                "password_change/done/",
                wrap(self.password_change_done, cacheable=True),
                name="password_change_done",
            ),
            path("autocomplete/", wrap(self.autocomplete_view), name="autocomplete"),
            path("jsi18n/", wrap(self.i18n_javascript, cacheable=True), name="jsi18n"),
            path(
                "r/<path:content_type_id>/<path:object_id>/",
                wrap(contenttype_views.shortcut),
                name="view_on_site",
            ),
        ] + self._get_extra_urls()

        # 2. Clean Model URLs & Legacy Redirects
        valid_app_labels = []
        for model, model_admin in self._registry.items():
            model_key = f"{model._meta.app_label}.{model._meta.model_name}"
            clean_route = self.MODEL_ROUTES.get(
                model_key, f"{model._meta.app_label}/{model._meta.model_name}"
            )

            # Route legacy ugly URL (e.g. games/game/) to clean URL (e.g. games/)
            if clean_route != f"{model._meta.app_label}/{model._meta.model_name}":
                legacy_prefix = f"{model._meta.app_label}/{model._meta.model_name}"
                urlpatterns += [
                    path(
                        f"{legacy_prefix}/<path:rest>",
                        RedirectView.as_view(
                            url=f"/{self.name}/{clean_route}/%(rest)s", permanent=True
                        ),
                    ),
                    path(
                        f"{legacy_prefix}/",
                        RedirectView.as_view(
                            url=f"/{self.name}/{clean_route}/", permanent=True
                        ),
                    ),
                ]

            # Primary clean route
            urlpatterns += [
                path(f"{clean_route}/", include(model_admin.urls)),
            ]

            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        # 3. App list fallback regex
        if valid_app_labels:
            regex = r"^(?P<app_label>" + "|".join(valid_app_labels) + ")/$"
            urlpatterns += [
                re_path(regex, wrap(self.app_index), name="app_list"),
            ]

        if self.final_catch_all_view:
            urlpatterns.append(re_path(r"(?P<url>.*)$", wrap(self.catch_all_view)))

        return urlpatterns


def setup_clean_admin():
    """Apply CleanUnfoldAdminSite to admin.site."""
    admin.site.__class__ = CleanUnfoldAdminSite
