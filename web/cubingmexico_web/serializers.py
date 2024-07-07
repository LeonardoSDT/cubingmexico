from rest_framework import serializers
from .models import StateTeam, RanksAverage, RanksSingle

class StateTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateTeam
        fields = '__all__'

class SingleRankSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    rank_type = serializers.SerializerMethodField()

    class Meta:
        model = RanksSingle
        fields = ['rank_type', 'person_id', 'event_id', 'best', 'rank']

    def get_rank(self, obj):
        return {
            'world': obj.world_rank,
            'continent': obj.continent_rank,
            'country': obj.country_rank,
            # 'state': obj.stateranksaverage_set.first().rank if obj.stateranksaverage_set.exists() else None
        }

    def get_rank_type(self, obj):
        return 'single'
    
class AverageRankSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    rank_type = serializers.SerializerMethodField()

    class Meta:
        model = RanksAverage
        fields = ['rank_type', 'person_id', 'event_id', 'best', 'rank']

    def get_rank(self, obj):
        return {
            'world': obj.world_rank,
            'continent': obj.continent_rank,
            'country': obj.country_rank,
            # 'state': obj.stateranksaverage_set.first().rank if obj.stateranksaverage_set.exists() else None
        }

    def get_rank_type(self, obj):
        return 'average'