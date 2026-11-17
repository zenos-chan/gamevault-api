from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from games.models import ApiUserProfile, Game


class GameDatabaseAPITests(APITestCase):
    def setUp(self):
        # 1. Create a Game
        self.game = Game.objects.create(
            title='Cyber Runner 2099',
            genre='ACTION',
            description='Cyberpunk endless runner in neon cities',
            developer='Neon Bytes Studio',
            publisher='Cybernetic Arts',
            rating=4.8,
            platforms=['PC', 'PS5', 'Xbox'],
            website='https://cyberrunner.example.com'
        )

        # 2. Create User and Token
        self.user = User.objects.create_user(
            username='subscriber1',
            email='sub1@example.com',
            password='password123'
        )
        self.token = Token.objects.get(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_api_root(self):
        url = reverse('project-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authentication', response.json())
        self.assertIn('endpoints', response.json())

    def test_user_registration(self):
        url = reverse('auth-register')
        payload = {
            'username': 'new_developer',
            'email': 'newdev@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.json())
        self.assertEqual(response.json()['tier'], 'FREE')
        self.assertEqual(response.json()['rate_limit_per_minute'], 60)

    def test_user_login(self):
        url = reverse('auth-login')
        payload = {
            'username': 'subscriber1',
            'password': 'password123'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['token'], self.token.key)

    def test_unauthenticated_request_is_denied(self):
        # Requesting without token must return 401
        url = reverse('game-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_game_list(self):
        url = reverse('game-list')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title'], 'Cyber Runner 2099')

    def test_get_game_details_by_id(self):
        url = reverse('game-detail', kwargs={'lookup_val': self.game.id})
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], 'Cyber Runner 2099')
        self.assertEqual(response.json()['rating'], '4.8')
        self.assertIn('PS5', response.json()['platforms'])

    def test_get_game_details_by_slug(self):
        url = reverse('game-detail', kwargs={'lookup_val': self.game.slug})
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.game.id)
        self.assertEqual(response.json()['title'], 'Cyber Runner 2099')

    def test_get_game_details_by_name_query(self):
        url = reverse('game-by-name') + '?name=Cyber Runner 2099'
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.game.id)

    def test_filter_games_by_name_parameter(self):
        url = reverse('game-list') + '?name=runner'
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)

    def test_current_user_profile(self):
        url = reverse('auth-me')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'subscriber1')
        self.assertEqual(response.json()['tier'], 'FREE')
        self.assertEqual(response.json()['rate_limit_per_minute'], 60)

    def test_rate_limiting_throttle(self):
        from django.core.cache import cache
        cache.clear()

        # Set a low limit to test throttling
        profile = self.user.api_profile
        profile.rate_limit_per_minute = 3
        profile.save()

        url = reverse('game-list')
        for i in range(3):
            res = self.client.get(url, **self.auth_headers)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 4th request must be throttled with 429 Too Many Requests
        res_throttled = self.client.get(url, **self.auth_headers)
        self.assertEqual(res_throttled.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_clean_admin_urls(self):
        self.assertEqual(reverse('admin:games_game_changelist'), '/admin/games/')
        self.assertEqual(reverse('admin:games_apiuserprofile_changelist'), '/admin/subscribers/')
        self.assertEqual(reverse('admin:authtoken_tokenproxy_changelist'), '/admin/tokens/')

        # 301 redirect from old legacy URL
        res = self.client.get('/admin/games/game/')
        self.assertEqual(res.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(res.url, '/admin/games/')
