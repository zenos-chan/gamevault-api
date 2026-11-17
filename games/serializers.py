from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import ApiUserProfile, Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id',
            'title',
            'slug',
            'genre',
            'description',
            'developer',
            'publisher',
            'release_date',
            'platforms',
            'rating',
            'website',
            'metadata',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    token = serializers.SerializerMethodField(read_only=True)
    rate_limit_per_minute = serializers.SerializerMethodField(read_only=True)
    tier = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'token', 'tier', 'rate_limit_per_minute']

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key

    def get_tier(self, obj):
        if hasattr(obj, 'api_profile'):
            return obj.api_profile.tier
        return 'FREE'

    def get_rate_limit_per_minute(self, obj):
        if hasattr(obj, 'api_profile'):
            return obj.api_profile.rate_limit_per_minute
        return 60


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    tier = serializers.CharField(read_only=True)
    rate_limit_per_minute = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must provide both username and password.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        token, _ = Token.objects.get_or_create(user=user)
        tier = 'FREE'
        rate_limit = 60
        if hasattr(user, 'api_profile'):
            tier = user.api_profile.tier
            rate_limit = user.api_profile.rate_limit_per_minute

        return {
            'username': user.username,
            'token': token.key,
            'user_id': user.id,
            'tier': tier,
            'rate_limit_per_minute': rate_limit,
        }


class ApiUserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ApiUserProfile
        fields = ['id', 'username', 'email', 'tier', 'rate_limit_per_minute', 'is_active', 'token', 'created_at']

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj.user)
        return token.key
