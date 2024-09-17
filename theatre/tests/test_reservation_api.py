from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Reservation


class UnauthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(reverse("theatre:reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user",
            password="testPass1"
        )
        self.client.force_authenticate(user=self.user)
        self.play = Play.objects.create(
            title="testPlay",
            description="test Description",
        )
        self.genre = Genre.objects.create(
            name="testGenre"
        )
        self.reservation = Reservation.objects.create(
            user=self.user
        )

    def test_reservation_list(self):
        response = self.client.get(reverse("theatre:reservation-list"))
        reservations = Reservation.objects.filter(user=self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), reservations.count())
