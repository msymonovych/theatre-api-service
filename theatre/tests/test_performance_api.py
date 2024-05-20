from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import TheatreHall, Performance, Play
from theatre.serializers import (
    PerformanceListSerializer,
    PerformanceSerializer,
    PerformanceDetailSerializer,
)


class UnauthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(reverse("theatre:performance-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test", password="testPass1"
        )
        self.client.force_authenticate(user=self.user)
        self.play = Play.objects.create(
            title="test",
            description="test",
        )
        self.theater_hall = TheatreHall.objects.create(
            name="test", rows=5, seats_in_row=5
        )
        self.performance = Performance.objects.create(
            show_time="2024-04-07T11:45:12.009Z",
            play=self.play,
            theatre_hall=self.theater_hall,
        )

    def test_performance_list(self):
        response = self.client.get(reverse("theatre:performance-list"))
        theatre_halls = Performance.objects.all()
        serializer = PerformanceListSerializer(theatre_halls, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(serializer.data))

    def test_performance_detail(self):
        response = self.client.get(
            reverse("theatre:performance-detail", kwargs={"pk": self.play.id})
        )
        performance = Performance.objects.get(pk=self.play.id)
        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_admin_rights_required(self):
        data = {"first_name": "John", "last_name": "Doe"}
        response = self.client.post(reverse("theatre:genre-list"), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            username="admin", password="adminPass1"
        )
        self.client.force_authenticate(user=self.user)
        self.play = Play.objects.create(
            title="test",
            description="test",
        )
        self.theater_hall = TheatreHall.objects.create(
            name="test", rows=5, seats_in_row=5
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theater_hall,
            show_time="2024-04-07T11:45:12.009Z",
        )

    def test_performance_create(self):
        data = {
            "show_time": "2024-04-07T11:45:12.009Z",
            "play": self.play.id,
            "theatre_hall": self.theater_hall.id,
        }
        response = self.client.post(reverse("theatre:performance-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        performance = Performance.objects.get(id=response.data["id"])
        serializer = PerformanceSerializer(performance)
        self.assertEqual(response.data, serializer.data)

    def test_performance_create_with_invalid_data(self):
        data = {
            "show_time": "invalid data",
            "play": "invalid data",
            "theatre_hall": "invalid data",
        }
        response = self.client.post(reverse("theatre:performance-list"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_performance_update(self):
        data = {"show_time": "2025-12-07T13:14:06.502Z", "play": 1, "theatre_hall": 1}
        response = self.client.put(
            reverse("theatre:performance-detail", kwargs={"pk": self.performance.id}),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        performance = Performance.objects.get(id=response.data["id"])
        serializer = PerformanceSerializer(performance)
        self.assertEqual(response.data, serializer.data)

    def test_performance_partial_update(self):
        data = {
            "show_time": "2025-01-01T13:14:06.502Z",
        }
        response = self.client.patch(
            reverse("theatre:performance-detail", kwargs={"pk": self.performance.id}),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        performance = Performance.objects.get(id=response.data["id"])
        serializer = PerformanceSerializer(performance)
        self.assertEqual(response.data, serializer.data)

    def test_performance_delete(self):
        response = self.client.delete(
            reverse("theatre:performance-detail", kwargs={"pk": self.performance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Performance.objects.count(), 0)
