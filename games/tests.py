from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from games.models import Game, Player, GameScore, Achievement, PlayerAchievement, GameSession


class GameAPITests(APITestCase):
    def setUp(self):
        self.game = Game.objects.create(
            title='Cosmic Defender',
            genre='SHOOTER',
            description='Arcade retro space shooter',
            max_players=1
        )
        self.player = Player.objects.create(
            username='star_lord',
            email='starlord@guardians.galaxy',
            gamer_tag='StarLord99'
        )
        self.achievement = Achievement.objects.create(
            game=self.game,
            name='First Blood',
            description='Destroy your first alien ship',
            points=20
        )

    def test_api_root(self):
        url = reverse('project-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', response.json())

    def test_list_games(self):
        url = reverse('game-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.json()['count'], 1)

    def test_create_game(self):
        url = reverse('game-list')
        payload = {
            'title': 'Quantum Racer',
            'genre': 'RACING',
            'description': 'Hyper-speed racing',
            'max_players': 4
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['slug'], 'quantum-racer')

    def test_submit_score_and_leaderboard(self):
        # Submit score
        score_url = reverse('gamescore-list')
        score_payload = {
            'game': self.game.id,
            'player': self.player.id,
            'score': 55000,
            'metadata': {'wave': 12, 'ships_destroyed': 140}
        }
        res_post = self.client.post(score_url, score_payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

        # Verify leaderboard
        lb_url = reverse('game-leaderboard', kwargs={'pk': self.game.id})
        res_lb = self.client.get(lb_url)
        self.assertEqual(res_lb.status_code, status.HTTP_200_OK)
        lb_data = res_lb.json()
        self.assertEqual(len(lb_data['leaderboard']), 1)
        self.assertEqual(lb_data['leaderboard'][0]['score'], 55000)
        self.assertEqual(lb_data['leaderboard'][0]['gamer_tag'], 'StarLord99')

    def test_unlock_achievement_and_xp(self):
        initial_xp = self.player.experience_points
        url = reverse('playerachievement-list')
        payload = {
            'player': self.player.id,
            'achievement': self.achievement.id
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.player.refresh_from_db()
        self.assertEqual(self.player.experience_points, initial_xp + self.achievement.points)

    def test_player_profile(self):
        url = reverse('player-profile', kwargs={'pk': self.player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['player']['gamer_tag'], 'StarLord99')

    def test_game_session_lifecycle(self):
        # Create session
        session_url = reverse('gamesession-list')
        session_res = self.client.post(session_url, {'game': self.game.id})
        self.assertEqual(session_res.status_code, status.HTTP_201_CREATED)
        session_id = session_res.json()['id']

        # Join session
        join_url = reverse('gamesession-join', kwargs={'pk': session_id})
        join_res = self.client.post(join_url, {'player_id': self.player.id})
        self.assertEqual(join_res.status_code, status.HTTP_200_OK)

        # Start session
        start_url = reverse('gamesession-start', kwargs={'pk': session_id})
        start_res = self.client.post(start_url)
        self.assertEqual(start_res.status_code, status.HTTP_200_OK)
        self.assertEqual(start_res.json()['session']['status'], 'IN_PROGRESS')

        # Finish session with winner
        finish_url = reverse('gamesession-finish', kwargs={'pk': session_id})
        finish_res = self.client.post(finish_url, {'winner_id': self.player.id})
        self.assertEqual(finish_res.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_res.json()['session']['status'], 'COMPLETED')
        self.assertEqual(finish_res.json()['session']['winner_gamer_tag'], 'StarLord99')
