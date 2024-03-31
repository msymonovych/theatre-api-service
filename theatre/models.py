from typing import Any

from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


class Play(models.Model):
    title = models.CharField(max_length=115)
    description = models.TextField()
    actors = models.ManyToManyField("Actor", related_name="plays")
    genres = models.ManyToManyField("Genre", related_name="plays")

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class Actor(models.Model):
    first_name = models.CharField(max_length=115)
    last_name = models.CharField(max_length=115)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Performance(models.Model):
    play = models.ForeignKey(
        Play, on_delete=models.CASCADE, related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall, on_delete=models.CASCADE, related_name="performances"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ("-show_time",)

    def __str__(self):
        return f"{self.play.title} {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ("-created_at",)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"

    @staticmethod
    def validate_ticket(
            seat: int,
            row: int,
            theatre_hall: TheatreHall,
            error_to_raise
    ) -> None:
        if not (1 <= seat <= theatre_hall.seats_in_row):
            raise error_to_raise(
                {
                    "seats": (
                        "seat must be in range "
                        f"[1, {theatre_hall.seats_in_row}]"
                    )
                }
            )
        elif not (1 <= row <= theatre_hall.rows):
            raise error_to_raise(
                {
                    "rows": f"row must be in range [1, {theatre_hall.rows}]"
                }
            )

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.row,
            self.performance.theatre_hall,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ("performance", "row", "seat")
