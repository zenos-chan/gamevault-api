from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from rest_framework.authtoken.models import Token


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
        ('SIMULATION', 'Simulation'),
        ('HORROR', 'Horror'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True, db_index=True)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default='ACTION')
    description = models.TextField(blank=True)
    developer = models.CharField(max_length=150, default='Indie Studio')
    publisher = models.CharField(max_length=150, blank=True, default='')
    release_date = models.DateField(null=True, blank=True)
    platforms = models.JSONField(default=list, blank=True, help_text='List of supported platforms, e.g. ["PC", "PS5"]')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5, help_text='Rating out of 5.0')
    website = models.URLField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True, help_text='Tags, system requirements, etc.')
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


class ApiUserProfile(models.Model):
    TIER_CHOICES = [
        ('FREE', 'Free Tier (60 calls/min)'),
        ('PRO', 'Pro Tier (300 calls/min)'),
        ('ENTERPRISE', 'Enterprise Tier (1200 calls/min)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_profile'
    )
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='FREE')
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.tier} - {self.rate_limit_per_minute}/min)"

    def save(self, *args, **kwargs):
        tier_limits = {
            'FREE': 60,
            'PRO': 300,
            'ENTERPRISE': 1200,
        }
        if self.tier in tier_limits and (not self.pk or 'tier' in kwargs.get('update_fields', [])):
            self.rate_limit_per_minute = tier_limits[self.tier]
        super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token_and_profile(sender, instance=None, created=False, **kwargs):
    """Automatically create an API auth token and ApiUserProfile whenever a user is created."""
    if created:
        Token.objects.get_or_create(user=instance)
        ApiUserProfile.objects.get_or_create(user=instance)
