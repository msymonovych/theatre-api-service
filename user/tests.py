from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


USER_ME_URL = reverse("user:manage")
USER_REGISTER_URL = reverse("user:create")
USER_LOGIN_URL = reverse("user:token_obtain_pair")


class UnauthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {"username": "test", "password": "testPass1"}

    def test_auth_required(self):
        response = self.client.get(USER_ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_new_user(self):
        response = self.client.post(USER_REGISTER_URL, self.data)
        users = get_user_model().objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(users.count(), 1)
        self.assertEqual(
            response.data["username"],
            users.first().username,
            self.data["username"]
        )

    def test_login_user_with_valid_data(self):
        self.client.post(USER_REGISTER_URL, self.data)
        response = self.client.post(USER_LOGIN_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("access", False))
        self.assertTrue(response.data.get("refresh", False))

    def test_login_user_with_invalid_data(self):
        self.client.post(USER_REGISTER_URL, self.data)
        self.data["username"] = "##$%^&* !"
        response = self.client.post(USER_LOGIN_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.data = {"username": "test", "password": "testPass1"}
        self.user = get_user_model().objects.create_user(**self.data)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_detail(self):
        response = self.client.get(USER_ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.data["username"])

    def test_user_update(self):
        new_username = "NewUsername"
        self.data["username"] = new_username
        response = self.client.put(USER_ME_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], new_username)
