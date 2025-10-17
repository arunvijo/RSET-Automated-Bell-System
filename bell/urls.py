# In bell/urls.py

from django.contrib import admin
# Make sure 'path' is imported
from django.urls import path, re_path as url
from web.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', login_user, name='login'),
    url(r'^$', login_user, name='root'),
    url(r'^home/', home, name='home'),
    url(r'^apply/', apply, name='apply'),
    url(r'^create/', create, name='create'),

    # ADD THIS LINE FOR THE EDIT FUNCTIONALITY
    path('profile/<int:profile_id>/edit/', edit_profile, name='edit_profile'),

    # ADD THIS NEW API URL PATTERN
    path('api/schedule/<str:block_name>/', get_schedule_api, name='api_get_schedule'),

    path('api/command/check/',check_for_command, name='check_for_command'),
    path('control/', system_control, name='system_control'),
    
    url(r'^profiles/', view_profiles, name='profiles'),
    url(r'^logout/', logout_user, name='logout'),
]