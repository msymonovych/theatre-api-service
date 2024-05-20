from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayListSerializer, PlayDetailSerializer


def sample_play(**params):
    defaults = {
        "title": "Sample Title",
        "description": "Sample Description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(reverse("theatre:play-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user", password="testPass1"
        )
        self.client.force_authenticate(user=self.user)
        self.play = sample_play(title="test1")
        sample_play()

    def test_play_list(self):
        response = self.client.get(reverse("theatre:play-list"))
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_play_detail(self):
        response = self.client.get(
            reverse("theatre:play-detail", kwargs={"pk": self.play.pk})
        )
        serializer = PlayDetailSerializer(self.play, many=False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_play_by_genres(self):
        genre1 = Genre.objects.create(name="Genre 1")
        genre2 = Genre.objects.create(name="Genre 2")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        response = self.client.get(
            reverse("theatre:play-list"), {"genres": f"{genre1.id},{genre2.id}"}
        )

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(self.play)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_play_by_actors(self):
        actor1 = Actor.objects.create(first_name="Actor 1", last_name="test")
        actor2 = Actor.objects.create(first_name="Actor 2", last_name="test")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        response = self.client.get(
            reverse("theatre:play-list"), {"actors": f"{actor1.id},{actor2.id}"}
        )

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(self.play)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_play_by_title(self):
        play1 = sample_play(title="Play Target")
        play2 = sample_play(title="Another Play")

        res = self.client.get(reverse("theatre:play-list"), {"title": "play"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(self.play)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_admin_rights_required(self):
        data = {"title": "test", "description": "test description"}
        response = self.client.post(reverse("theatre:play-list"), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            username="admin", password="adminPass1"
        )
        self.client.force_authenticate(user=self.admin)

    def test_play_create(self):
        genre = Genre.objects.create(name="Test Genre")
        actor = Actor.objects.create(first_name="Test", last_name="Actor")
        data = {
            "title": "test",
            "description": "test description",
            "actors": [actor.id],
            "genres": [genre.id],
        }
        response = self.client.post(
            reverse("theatre:play-list"),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(id=response.data["id"])
        self.assertEqual(play.title, data["title"])
