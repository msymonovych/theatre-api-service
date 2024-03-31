from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from theatre.models import (
    Play,
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = "__all__"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actors",
            "genres",
        )


class PlayImageSerializer(PlaySerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


class PlayListSerializer(serializers.ModelSerializer):
    actors = serializers.SlugRelatedField(
        many=True, slug_field="full_name", read_only=True
    )
    genres = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = Play
        fields = ("id", "title", "actors", "genres", "image")


class PlayDetailSerializer(PlaySerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actors",
            "genres",
            "image",
        )


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = "__all__"


class PerformanceListSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    theatre_hall_name = serializers.CharField(
        source="theatre_hall.name", read_only=True
    )
    theatre_hall_capacity = serializers.IntegerField(
        source="theatre_hall.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)
    play_image = serializers.ImageField(source="play.image", read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "play_title",
            "theatre_hall_name",
            "theatre_hall_capacity",
            "show_time",
            "tickets_available",
            "play_image",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            row=attrs["row"],
            seat=attrs["seat"],
            theatre_hall=attrs["performance"].theatre_hall,
            error_to_raise=ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(many=False, read_only=True)
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    taken_seats = TicketSeatsSerializer(
        many=True, read_only=True, source="tickets"
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "taken_seats", "show_time")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_null=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
