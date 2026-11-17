from datetime import date
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token
from games.models import ApiUserProfile, Game


class Command(BaseCommand):
    help = 'Seeds database with realistic game catalog and ensures admin user with token exists'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Game Database...")

        # 1. Create Sample Games
        games_data = [
            {
                'title': 'Cyber Runner 2099',
                'genre': 'ACTION',
                'description': 'A high-octane cyberpunk endless runner set in neon-drenched megacities with synthwave soundtrack.',
                'developer': 'Neon Bytes Studio',
                'publisher': 'Cybernetic Arts',
                'release_date': date(2025, 4, 15),
                'platforms': ['PC', 'PlayStation 5', 'Xbox Series X'],
                'rating': 4.8,
                'website': 'https://cyberrunner2099.example.com',
                'metadata': {'engine': 'Unreal Engine 5', 'languages': ['English', 'Japanese', 'German']},
            },
            {
                'title': 'Shadow Tactics: Arena',
                'genre': 'STRATEGY',
                'description': 'Turn-based tactical arena where ninja stealth meets arcane elemental spells.',
                'developer': 'Tactical Forge',
                'publisher': 'Apex Strategy Interactive',
                'release_date': date(2024, 11, 20),
                'platforms': ['PC', 'Nintendo Switch'],
                'rating': 4.6,
                'website': 'https://shadowtactics.example.com',
                'metadata': {'engine': 'Unity', 'multiplayer': True},
            },
            {
                'title': 'Galaxy Drift',
                'genre': 'RACING',
                'description': 'Anti-gravity interstellar racing game with customizable hyper-craft and wormhole shortcuts.',
                'developer': 'AeroVelocity',
                'publisher': 'Speedway Cosmos',
                'release_date': date(2025, 1, 10),
                'platforms': ['PC', 'PlayStation 5', 'Xbox Series X', 'Mobile'],
                'rating': 4.9,
                'website': 'https://galaxydrift.example.com',
                'metadata': {'vr_support': True, 'engine': 'Custom Aero Engine'},
            },
            {
                'title': 'Mystic Dungeon Crawler',
                'genre': 'RPG',
                'description': 'Procedural rogue-lite isometric dungeon exploration with deep alchemy and spell-crafting.',
                'developer': 'Loot & Level',
                'publisher': 'Indie Sanctuary',
                'release_date': date(2024, 8, 5),
                'platforms': ['PC', 'Nintendo Switch', 'macOS'],
                'rating': 4.7,
                'website': 'https://mysticdungeon.example.com',
                'metadata': {'co-op': True, 'gamepad_support': True},
            },
            {
                'title': 'Valkyrie Protocol',
                'genre': 'SHOOTER',
                'description': 'Futuristic co-op extraction shooter with mech suits and zero-gravity gunplay.',
                'developer': 'Titanworks Studios',
                'publisher': 'Nova Prime Games',
                'release_date': date(2025, 6, 30),
                'platforms': ['PC', 'PlayStation 5'],
                'rating': 4.5,
                'website': 'https://valkyrieprotocol.example.com',
                'metadata': {'engine': 'Unreal Engine 5', 'pvp': True},
            },
        ]

        for g_data in games_data:
            game, created = Game.objects.get_or_create(title=g_data['title'], defaults=g_data)
            action = "Created" if created else "Found existing"
            self.stdout.write(f"  - {action} game: {game.title} (ID: {game.id}, Slug: {game.slug})")

        # 2. Create Admin Superuser & Token
        User = get_user_model()
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com'}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write("  - Created default superuser: admin (password: admin123)")

        admin_token, _ = Token.objects.get_or_create(user=admin_user)
        admin_profile, _ = ApiUserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'tier': 'ENTERPRISE', 'rate_limit_per_minute': 1200}
        )

        # 3. Create Sample Demo User for API testing
        demo_user, created = User.objects.get_or_create(
            username='gamer_dev',
            defaults={'email': 'dev@example.com'}
        )
        if created:
            demo_user.set_password('devpass123')
            demo_user.save()
            self.stdout.write("  - Created demo API user: gamer_dev (password: devpass123)")

        demo_token, _ = Token.objects.get_or_create(user=demo_user)
        demo_profile, _ = ApiUserProfile.objects.get_or_create(
            user=demo_user,
            defaults={'tier': 'FREE', 'rate_limit_per_minute': 60}
        )

        self.stdout.write(self.style.SUCCESS(f"\nSeeding complete!"))
        self.stdout.write(f"Admin Token: {admin_token.key}")
        self.stdout.write(f"Demo User Token: {demo_token.key}")
