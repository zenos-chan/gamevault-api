from django.contrib import admin
from django.urls import include, path
from games.web_views import (
    dashboard_view,
    landing_page_view,
    login_view,
    logout_view,
    signup_view,
)

urlpatterns = [
    # Frontend Pages
    path('', landing_page_view, name='landing-page'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Admin Portal
    path('admin/', admin.site.urls),

    # REST API Endpoints
    path('api/', include('games.urls')),
]
