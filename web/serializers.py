# In web/serializers.py
from rest_framework import serializers
from .models import Profile, Bell

class BellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bell
        fields = [
            'time', 'is_long', 'play_anthem', 
            'monday', 'tuesday', 'wednesday', 'thursday', 
            'friday', 'saturday', 'sunday'
        ]

class ProfileSerializer(serializers.ModelSerializer):
    # This nests all the bells inside their parent profile.
    bells = BellSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['name', 'bells']