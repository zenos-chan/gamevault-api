from datetime import date
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from games.models import Game, Player, GameScore, Achievement, PlayerAchievement, GameSession


class Command(BaseCommand):
    help = 'Seeds database with realistic sample games, players, achievements, and scores'

    def handle(self, *args, **options):
        self.stdout.write("Seeding game API database...")

        # 1. Create Games
        games_data = [
            {
                'title': 'Cyber Runner 2099',
                'genre': 'ACTION',
                'description': 'A fast-paced futuristic endless cyberpunk runner with neon aesthetics.',
                'developer': 'Neon Bytes Studio',
                'release_date': date(2025, 4, 15),
                'max_players': 1,
            },
            {
                'title': 'Shadow Tactics: Arena',
                'genre': 'STRATEGY',
                'description': 'Multiplayer turn-based tactical arena where ninjas and sorcerers clash.',
                'developer': 'Tactical Forge',
                'release_date': date(2024, 11, 20),
                'max_players': 4,
            },
            {
                'title': 'Galaxy Drift',
                'genre': 'RACING',
                'description': 'Anti-gravity interstellar racing game across asteroid belts and wormholes.',
                'developer': 'AeroVelocity',
                'release_date': date(2025, 1, 10),
                'max_players': 8,
            },
            {
                'title': 'Mystic Dungeon Crawler',
                'genre': 'RPG',
                'description': 'Procedural rogue-lite dungeon exploration with elemental magic crafting.',
                'developer': 'Loot & Level',
                'release_date': date(2024, 8, 5),
                'max_players': 2,
            },
        ]

        created_games = {}
        for g_data in games_data:
            game, created = Game.objects.get_or_create(title=g_data['title'], defaults=g_data)
            created_games[game.title] = game
            action = "Created" if created else "Found existing"
            self.stdout.write(f"  - {action} game: {game.title}")

        # 2. Create Players
        players_data = [
            {'username': 'apex_hunter', 'email': 'hunter@example.com', 'gamer_tag': 'Valkyrie99', 'status': 'ONLINE'},
            {'username': 'pixel_knight', 'email': 'knight@example.com', 'gamer_tag': 'SirPixel', 'status': 'IN_GAME'},
            {'username': 'quantum_coder', 'email': 'coder@example.com', 'gamer_tag': 'NullPointer', 'status': 'ONLINE'},
            {'username': 'shadow_strike', 'email': 'strike@example.com', 'gamer_tag': 'GhostNinja', 'status': 'OFFLINE'},
        ]

        created_players = {}
        for p_data in players_data:
            player, created = Player.objects.get_or_create(username=p_data['username'], defaults=p_data)
            created_players[player.username] = player
            action = "Created" if created else "Found existing"
            self.stdout.write(f"  - {action} player: {player.gamer_tag}")

        # 3. Create Achievements
        cyber_runner = created_games['Cyber Runner 2099']
        galaxy_drift = created_games['Galaxy Drift']

        achievements_data = [
            (cyber_runner, 'Speed Demon', 'Reach 500 km/h in Sector 4', 25, 'flash'),
            (cyber_runner, 'Flawless Run', 'Complete level 10 without hitting any obstacles', 50, 'shield'),
            (cyber_runner, 'First Step', 'Finish the tutorial run', 10, 'footsteps'),
            (galaxy_drift, 'Wormhole Master', 'Drift through 5 consecutive cosmic portals', 30, 'rocket'),
            (galaxy_drift, 'Podium Finisher', 'Finish in 1st place in a multiplayer race', 40, 'trophy'),
        ]

        created_achievements = []
        for game, name, desc, pts, icon in achievements_data:
            ach, created = Achievement.objects.get_or_create(
                game=game,
                name=name,
                defaults={'description': desc, 'points': pts, 'badge_icon': icon}
            )
            created_achievements.append(ach)

        # 4. Create Scores
        scores_data = [
            (cyber_runner, created_players['apex_hunter'], 125400, {'stage': 12, 'difficulty': 'Hard'}),
            (cyber_runner, created_players['pixel_knight'], 98200, {'stage': 9, 'difficulty': 'Normal'}),
            (cyber_runner, created_players['quantum_coder'], 143500, {'stage': 15, 'difficulty': 'Insane'}),
            (galaxy_drift, created_players['apex_hunter'], 87600, {'track': 'Nebula Ridge', 'lap_time': '01:14.32'}),
            (galaxy_drift, created_players['shadow_strike'], 91200, {'track': 'Nebula Ridge', 'lap_time': '01:11.89'}),
        ]

        for game, player, score_val, meta in scores_data:
            GameScore.objects.get_or_create(
                game=game,
                player=player,
                score=score_val,
                defaults={'metadata': meta}
            )
            player.add_xp(score_val // 1000)

        # 5. Unlock Achievements
        for ach in created_achievements[:3]:
            player = created_players['apex_hunter']
            pa, created = PlayerAchievement.objects.get_or_create(player=player, achievement=ach)
            if created:
                player.add_xp(ach.points)

        # 6. Create Sample Multiplayer Session
        arena = created_games['Shadow Tactics: Arena']
        session, created = GameSession.objects.get_or_create(
            game=arena,
            room_code='TACTIC01',
            defaults={'status': 'WAITING'}
        )
        session.players.add(created_players['apex_hunter'], created_players['pixel_knight'])

        # 7. Create Admin Superuser if not exists
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write("  - Created default superuser: admin (password: admin123)")

        self.stdout.write(self.style.SUCCESS("Successfully seeded game database!"))
