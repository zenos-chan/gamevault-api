from rest_framework import serializers
from .models import Game, Player, GameScore, Achievement, PlayerAchievement, GameSession


class AchievementSerializer(serializers.ModelSerializer):
    game_title = serializers.ReadOnlyField(source='game.title')

    class Meta:
        model = Achievement
        fields = ['id', 'game', 'game_title', 'name', 'description', 'points', 'badge_icon', 'created_at']


class PlayerAchievementSerializer(serializers.ModelSerializer):
    gamer_tag = serializers.ReadOnlyField(source='player.gamer_tag')
    achievement_name = serializers.ReadOnlyField(source='achievement.name')
    achievement_points = serializers.ReadOnlyField(source='achievement.points')
    badge_icon = serializers.ReadOnlyField(source='achievement.badge_icon')

    class Meta:
        model = PlayerAchievement
        fields = ['id', 'player', 'gamer_tag', 'achievement', 'achievement_name', 'achievement_points', 'badge_icon', 'unlocked_at']

    def create(self, validated_data):
        player_achievement = super().create(validated_data)
        # Award XP corresponding to achievement points
        player = player_achievement.player
        player.add_xp(player_achievement.achievement.points)
        return player_achievement


class GameScoreSerializer(serializers.ModelSerializer):
    player_gamer_tag = serializers.ReadOnlyField(source='player.gamer_tag')
    game_title = serializers.ReadOnlyField(source='game.title')

    class Meta:
        model = GameScore
        fields = ['id', 'game', 'game_title', 'player', 'player_gamer_tag', 'score', 'metadata', 'achieved_at']

    def create(self, validated_data):
        score_entry = super().create(validated_data)
        # Award base XP for playing and recording a score (10 XP + 1 XP per 1,000 score, capped at 100 XP per submit)
        base_xp = 10
        extra_xp = min(int(score_entry.score // 1000), 90)
        score_entry.player.add_xp(base_xp + extra_xp)
        return score_entry


class GameSerializer(serializers.ModelSerializer):
    scores_count = serializers.IntegerField(source='scores.count', read_only=True)
    achievements_count = serializers.IntegerField(source='achievements.count', read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'slug', 'genre', 'description', 'developer',
            'release_date', 'max_players', 'is_active', 'scores_count',
            'achievements_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class PlayerSerializer(serializers.ModelSerializer):
    unlocked_achievements_count = serializers.IntegerField(source='unlocked_achievements.count', read_only=True)
    total_scores_recorded = serializers.IntegerField(source='scores.count', read_only=True)

    class Meta:
        model = Player
        fields = [
            'id', 'username', 'email', 'gamer_tag', 'level', 'experience_points',
            'status', 'unlocked_achievements_count', 'total_scores_recorded',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['level', 'experience_points', 'created_at', 'updated_at']


class GameSessionSerializer(serializers.ModelSerializer):
    game_title = serializers.ReadOnlyField(source='game.title')
    players_count = serializers.IntegerField(source='players.count', read_only=True)
    winner_gamer_tag = serializers.ReadOnlyField(source='winner.gamer_tag')

    class Meta:
        model = GameSession
        fields = [
            'id', 'room_code', 'game', 'game_title', 'status', 'players',
            'players_count', 'winner', 'winner_gamer_tag', 'started_at',
            'ended_at', 'created_at'
        ]
        read_only_fields = ['room_code', 'created_at']
