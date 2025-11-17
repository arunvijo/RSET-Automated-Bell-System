# web/admin.py

from django.contrib import admin
from .models import Profile, Bell, main_current, pg_current, ke_current

# Register your new models to make them accessible in the admin interface
admin.site.register(Profile)
admin.site.register(Bell)
admin.site.register(main_current)
admin.site.register(pg_current)
admin.site.register(ke_current)