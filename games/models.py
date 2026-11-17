import uuid
from django.db import models
from django.utils.text import slugify


class Game(models.Model):
    GENRE_CHOICES = [
        ('ACTION', 'Action'),
        ('ADVENTURE', 'Adventure'),
        ('RPG', 'Role Playing Game'),
        ('STRATEGY', 'Strategy'),
        ('PUZZLE', 'Puzzle'),
        ('RACING', 'Racing'),
        ('SPORTS', 'Sports'),
        ('SHOOTER', 'Shooter'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default='ACTION')
    description = models.TextField(blank=True)
    developer = models.CharField(max_length=100, default='Indie Studio')
    release_date = models.DateField(null=True, blank=True)
    max_players = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'game'
            slug = base_slug
            counter = 1
            while Game.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Player(models.Model):
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('IN_GAME', 'In Game'),
    ]

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    gamer_tag = models.CharField(max_length=50, unique=True)
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-experience_points', 'username']

    def add_xp(self, xp_amount):
        """Add XP to player and automatically level up (100 XP per level)."""
        self.experience_points += xp_amount
        new_level = (self.experience_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save(update_fields=['experience_points', 'level', 'updated_at'])

    def __str__(self):
        return f"{self.gamer_tag} (Lv. {self.level})"


class GameScore(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    score = models.BigIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-achieved_at']

    def __str__(self):
        return f"{self.player.gamer_tag} - {self.game.title}: {self.score}"


class Achievement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.PositiveIntegerField(default=10)
    badge_icon = models.CharField(max_length=50, default='trophy')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game', 'name')
        ordering = ['game', 'points']

    def __str__(self):
        return f"{self.game.title} - {self.name} ({self.points} pts)"


class PlayerAchievement(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='unlocked_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='unlocked_by')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'achievement')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.player.gamer_tag} unlocked {self.achievement.name}"


class GameSession(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Waiting for Players'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    room_code = models.CharField(max_length=16, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    players = models.ManyToManyField(Player, related_name='game_sessions', blank=True)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_sessions')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.room_code} - {self.game.title} ({self.status})"
