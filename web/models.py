# web/models.py
from django.db import models

# This model just stores the name of a bell schedule.
class Profile(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# This model stores a SINGLE bell event.
class Bell(models.Model):
    # This is the crucial relationship: Each Bell belongs to a Profile.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bells')
    
    # --- Bell Details ---
    time = models.TimeField()
    is_long = models.BooleanField(default=False)
    play_anthem = models.BooleanField(default=False)
    
    # --- Active Days (a much cleaner way to store this) ---
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    class Meta:
        # This ensures bells are always shown in chronological order.
        ordering = ['time']

    def __str__(self):
        # Provides a helpful name in the Django admin area.
        return f"{self.profile.name} at {self.time.strftime('%I:%M %p')}"

# These models are for the 'apply' functionality and can remain.
# We'll rename the old 'blk' model that they referenced.
class main_current(models.Model):
    name = models.CharField(max_length=50, unique=True)

class pg_current(models.Model):
    name = models.CharField(max_length=50, unique=True)

class ke_current(models.Model):
    name = models.CharField(max_length=50, unique=True)