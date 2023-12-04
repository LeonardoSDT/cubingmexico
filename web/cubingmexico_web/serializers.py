from rest_framework import serializers
from .models import StateTeam

class StateTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateTeam
        fields = '__all__'