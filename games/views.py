from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ApiUserProfile, Game
from .serializers import (
    ApiUserProfileSerializer,
    GameSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
)
from .throttles import PerMinuteUserRateThrottle


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Game Database API.
    Requires authentication via Token: `Authorization: Token <your_token>`.
    Subject to per-minute rate limits.
    """
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PerMinuteUserRateThrottle]
    lookup_field = 'lookup_val'

    def get_object(self):
        """
        Supports retrieving a game by ID, by exact slug, or by title!
        Example:
          /api/games/1/
          /api/games/cyber-runner-2099/
          /api/games/Cyber Runner 2099/
        """
        lookup_val = self.kwargs.get(self.lookup_field, '').strip()
        queryset = self.filter_queryset(self.get_queryset())

        # If numeric, lookup by ID first
        if lookup_val.isdigit():
            return get_object_or_404(queryset, id=int(lookup_val))

        # Lookup by slug or case-insensitive title
        game = queryset.filter(Q(slug__iexact=lookup_val) | Q(title__iexact=lookup_val)).first()
        if game is not None:
            return game

        # Fallback partial title match if single match
        matching_games = queryset.filter(title__icontains=lookup_val)
        if matching_games.count() == 1:
            return matching_games.first()

        return get_object_or_404(queryset, slug__iexact=lookup_val)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Search / filter by name or title
        name = self.request.query_params.get('name') or self.request.query_params.get('title')
        genre = self.request.query_params.get('genre')
        developer = self.request.query_params.get('developer')
        platform = self.request.query_params.get('platform')

        if name:
            queryset = queryset.filter(Q(title__icontains=name) | Q(slug__icontains=name))
        if genre:
            queryset = queryset.filter(genre__iexact=genre)
        if developer:
            queryset = queryset.filter(developer__icontains=developer)
        if platform:
            queryset = queryset.filter(platforms__icontains=platform)

        return queryset

    @action(detail=False, methods=['get'], url_path='by-name')
    def by_name(self, request):
        """
        Explicit search endpoint by name query param:
        GET /api/games/by-name/?name=Cyber Runner
        """
        name = request.query_params.get('name', '').strip()
        if not name:
            return Response(
                {'error': "Query parameter 'name' is required. Example: ?name=Cyber+Runner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        game = self.get_queryset().filter(Q(title__iexact=name) | Q(slug__iexact=name)).first()
        if not game:
            # Fallback to partial match
            game = self.get_queryset().filter(title__icontains=name).first()

        if not game:
            return Response({'error': f"Game with name '{name}' not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(GameSerializer(game).data)


class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for new users to sign up and instantly receive an API access token.
    POST /api/auth/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(generics.GenericAPIView):
    """
    Public endpoint for existing users to retrieve their API access token.
    POST /api/auth/token/ or POST /api/auth/login/
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CurrentUserProfileView(generics.RetrieveAPIView):
    """
    Protected endpoint to inspect your user subscription, API tier, token, and rate limit.
    GET /api/auth/me/
    """
    serializer_class = ApiUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = ApiUserProfile.objects.get_or_create(user=self.request.user)
        return profile
