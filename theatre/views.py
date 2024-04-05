from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.models import (
    Play,
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation
)
from theatre.serializers import (
    PlaySerializer,
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationListSerializer, PlayImageSerializer,
)


class PlayViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly,]

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genre")
        actors = self.request.query_params.get("actors")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if actors:
            actors_ids = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return self.serializer_class

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload-image",
        permission_classes=[IsAdminUser]
    )
    def upload_image(self, request, pk=None):
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by title (ex. ?title=Title)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="genres",
                description="Filter by genre id (ex. ?genres=1,2)",
                type={"type": "list", "items":{"type": "number"}}
            ),
            OpenApiParameter(
                name="actors",
                description="Filter by actors id (ex. ?actors=1,2)",
                type={"type": "list", "items": {"type": "number"}}
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly,]


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly,]


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly,]


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly,]

    def get_queryset(self):
        queryset = self.queryset.select_related("play", "theatre_hall")

        date = self.request.query_params.get("date")
        play = self.request.query_params.get("play")

        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("theatre_hall__rows")
                    * F("theatre_hall__seats_in_row")
                    - Count("tickets")
                )
            )

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play:
            queryset = queryset.filter(play__id=play)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                description=(
                        "Filter by show time date "
                        "(ex. ?date=2020-01-10)"
                ),
                type=OpenApiTypes.DATE
            ),
            OpenApiParameter(
                name="play",
                description="Filter by play id (ex. ?play=1)",
                type=OpenApiTypes.INT
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall"
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
