from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Achievement, Game, GameScore, GameSession, Player, PlayerAchievement
from .serializers import (
    AchievementSerializer,
    GameScoreSerializer,
    GameSerializer,
    GameSessionSerializer,
    PlayerAchievementSerializer,
    PlayerSerializer,
)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().prefetch_related('scores', 'achievements')
    serializer_class = GameSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.query_params.get('genre')
        active = self.request.query_params.get('active')
        if genre:
            queryset = queryset.filter(genre__iexact=genre)
        if active is not None:
            is_active = active.lower() in ['true', '1']
            queryset = queryset.filter(is_active=is_active)
        return queryset

    @action(detail=True, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request, pk=None):
        """Get the top ranked scores for this game."""
        game = self.get_object()
        limit = int(request.query_params.get('limit', 10))
        top_scores = (
            GameScore.objects.filter(game=game)
            .select_related('player')
            .order_by('-score', '-achieved_at')[:limit]
        )

        leaderboard_data = []
        for rank, entry in enumerate(top_scores, start=1):
            leaderboard_data.append({
                'rank': rank,
                'score_id': entry.id,
                'score': entry.score,
                'player_id': entry.player.id,
                'gamer_tag': entry.player.gamer_tag,
                'metadata': entry.metadata,
                'achieved_at': entry.achieved_at,
            })

        return Response({
            'game_id': game.id,
            'game_title': game.title,
            'total_entries': len(leaderboard_data),
            'leaderboard': leaderboard_data,
        })

    @action(detail=True, methods=['get'], url_path='achievements')
    def achievements(self, request, pk=None):
        """List all achievements for this game."""
        game = self.get_object()
        achievements = game.achievements.all()
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all().prefetch_related('unlocked_achievements', 'scores')
    serializer_class = PlayerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)
        return queryset

    @action(detail=True, methods=['get'], url_path='profile')
    def profile(self, request, pk=None):
        """Full player summary with unlocked badges and recent scores."""
        player = self.get_object()
        recent_scores = (
            GameScore.objects.filter(player=player)
            .select_related('game')
            .order_by('-achieved_at')[:5]
        )
        unlocked = (
            PlayerAchievement.objects.filter(player=player)
            .select_related('achievement', 'achievement__game')
            .order_by('-unlocked_at')
        )

        return Response({
            'player': PlayerSerializer(player).data,
            'recent_scores': [
                {
                    'id': score.id,
                    'game_title': score.game.title,
                    'score': score.score,
                    'achieved_at': score.achieved_at,
                }
                for score in recent_scores
            ],
            'unlocked_achievements': [
                {
                    'achievement_id': item.achievement.id,
                    'game': item.achievement.game.title,
                    'name': item.achievement.name,
                    'points': item.achievement.points,
                    'badge_icon': item.achievement.badge_icon,
                    'unlocked_at': item.unlocked_at,
                }
                for item in unlocked
            ],
        })

    @action(detail=True, methods=['post'], url_path='status')
    def update_status(self, request, pk=None):
        """Update player status (ONLINE, OFFLINE, IN_GAME)."""
        player = self.get_object()
        new_status = request.data.get('status', '').upper()
        valid_statuses = dict(Player.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {'error': f"Invalid status. Must be one of: {list(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        player.status = new_status
        player.save(update_fields=['status', 'updated_at'])
        return Response({'message': f"Status updated to {new_status}", 'player': PlayerSerializer(player).data})


class GameScoreViewSet(viewsets.ModelViewSet):
    queryset = GameScore.objects.all().select_related('game', 'player')
    serializer_class = GameScoreSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        game_id = self.request.query_params.get('game')
        player_id = self.request.query_params.get('player')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        return queryset


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all().select_related('game')
    serializer_class = AchievementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        game_id = self.request.query_params.get('game')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        return queryset


class PlayerAchievementViewSet(viewsets.ModelViewSet):
    queryset = PlayerAchievement.objects.all().select_related('player', 'achievement', 'achievement__game')
    serializer_class = PlayerAchievementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        player_id = self.request.query_params.get('player')
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        return queryset


class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all().select_related('game', 'winner').prefetch_related('players')
    serializer_class = GameSessionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        game_id = self.request.query_params.get('game')
        status_param = self.request.query_params.get('status')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)
        return queryset

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        """Add a player to an active waiting session."""
        session = self.get_object()
        if session.status != 'WAITING':
            return Response(
                {'error': f"Cannot join a session with status '{session.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player_id = request.data.get('player_id')
        if not player_id:
            return Response({'error': 'player_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(pk=player_id)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

        if session.players.count() >= session.game.max_players:
            return Response({'error': 'Session is full'}, status=status.HTTP_400_BAD_REQUEST)

        session.players.add(player)
        return Response({
            'message': f"Player '{player.gamer_tag}' joined session {session.room_code}",
            'session': GameSessionSerializer(session).data,
        })

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        """Mark session as IN_PROGRESS."""
        session = self.get_object()
        if session.status != 'WAITING':
            return Response(
                {'error': f"Session cannot be started from status '{session.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = 'IN_PROGRESS'
        session.started_at = timezone.now()
        session.save(update_fields=['status', 'started_at'])
        return Response({
            'message': f"Session {session.room_code} started",
            'session': GameSessionSerializer(session).data,
        })

    @action(detail=True, methods=['post'], url_path='finish')
    def finish(self, request, pk=None):
        """Mark session as COMPLETED and award winner if specified."""
        session = self.get_object()
        if session.status != 'IN_PROGRESS':
            return Response(
                {'error': f"Only sessions IN_PROGRESS can be finished (current status: '{session.status}')."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        winner_id = request.data.get('winner_id')
        if winner_id:
            try:
                winner = session.players.get(pk=winner_id)
                session.winner = winner
                # Bonus XP for winning a multiplayer session
                winner.add_xp(50)
            except Player.DoesNotExist:
                return Response({'error': 'Winner must be one of the players in this session.'}, status=status.HTTP_400_BAD_REQUEST)

        session.status = 'COMPLETED'
        session.ended_at = timezone.now()
        session.save(update_fields=['status', 'winner', 'ended_at'])
        return Response({
            'message': f"Session {session.room_code} completed",
            'session': GameSessionSerializer(session).data,
        })
