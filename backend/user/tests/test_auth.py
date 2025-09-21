from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import User


class JWTAuthTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.obtain_pair_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.blacklist_url = reverse("token_blacklist")
        self.profile_url = reverse("user-me")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", is_active=True
        )

    def _get_token_pair(self, response):
        cookies = response.cookies
        access = response.json().get("access", None)
        refresh = (
            cookies.get("refresh_token").value if "refresh_token" in cookies else None
        )
        return access, refresh

    def test_obtain_token_pair_success(self):
        response = self.client.post(
            self.obtain_pair_url,
            data={"email": self.user.email, "password": "testpass123"},
        )
        access, refresh = self._get_token_pair(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(access)
        self.assertIsNotNone(refresh)

    def test_obtain_token_pair_invalid_credentials_fails(self):
        response = self.client.post(
            self.obtain_pair_url,
            data={"email": self.user.email, "password": "wrongpass"},
        )
        access, refresh = self._get_token_pair(response)
        self.assertEqual(response.status_code, 401)
        self.assertIsNone(access)
        self.assertIsNone(refresh)

    def test_refresh_token_success(self):
        #  First, obtain a valid refresh in cookies
        response = self.client.post(
            self.obtain_pair_url,
            data={"email": self.user.email, "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 200)
        access_1, refresh_1 = self._get_token_pair(response)
        self.assertIsNotNone(access_1)
        self.assertIsNotNone(refresh_1)

        # Second time, just request again since the refresh token is in cookies
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 200)
        access_2, refresh_2 = self._get_token_pair(response)
        self.assertIsNotNone(access_2)
        self.assertIsNotNone(refresh_2)

        self.assertNotEqual(access_1, access_2)

    def test_refresh_token_not_in_cookies_fails(self):
        # Note that the client cookies live during the test case, so must clear them
        self.client.cookies.clear()
        response = self.client.post(self.refresh_url)
        access, refresh = self._get_token_pair(response)
        self.assertEqual(response.status_code, 401)
        self.assertIsNone(access)
        self.assertIsNone(refresh)

    def test_access_protected_endpoint_success(self):
        #  First, obtain a valid access token
        response = self.client.post(
            self.obtain_pair_url,
            data={"email": self.user.email, "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 200)
        access, refresh = self._get_token_pair(response)
        self.assertIsNotNone(access)
        self.assertIsNotNone(refresh)

        # Access the protected endpoint with the access token in Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("email"), self.user.email)

    def test_blacklist_token_success(self):
        #  First, obtain a valid refresh in cookies
        response = self.client.post(
            self.obtain_pair_url,
            data={"email": self.user.email, "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 200)
        access_1, refresh_1 = self._get_token_pair(response)
        self.assertIsNotNone(access_1)
        self.assertIsNotNone(refresh_1)

        # Blacklist the refresh token
        response = self.client.post(self.blacklist_url)
        self.assertEqual(response.status_code, 200)

        # Try to use the blacklisted refresh token to get a new access token
        response = self.client.post(self.refresh_url)
        access, refresh = self._get_token_pair(response)
        self.assertEqual(response.status_code, 401)
        self.assertIsNone(access)
        self.assertIsNone(refresh)

    def test_blacklist_token_not_in_cookies_fails(self):
        # Note that the client cookies live during the test case, so must clear them
        self.client.cookies.clear()
        response = self.client.post(self.blacklist_url)
        self.assertEqual(response.status_code, 401)
