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
    

# Add this new model at the end of the file
class ClientCommand(models.Model):
    COMMAND_CHOICES = [
        ('AMP_ON', 'Amp On'),
        ('AMP_OFF', 'Amp Off'),
        ('TEST_BELL', 'Test Bell'),
    ]
    command = models.CharField(max_length=20, choices=COMMAND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    # This field will track if the client has seen and executed the command
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_command_display()} at {self.created_at}"

# These models are for the 'apply' functionality and can remain.
# We'll rename the old 'blk' model that they referenced.
class main_current(models.Model):
    name = models.CharField(max_length=50, unique=True)

class pg_current(models.Model):
    name = models.CharField(max_length=50, unique=True)

class ke_current(models.Model):
    name = models.CharField(max_length=50, unique=True)