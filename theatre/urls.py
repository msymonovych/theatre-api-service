from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    PlayViewSet,
    ActorViewSet,
    GenreViewSet,
    TheatreHallViewSet, PerformanceViewSet, ReservationViewSet, TicketViewSet
)

router = routers.DefaultRouter()
router.register("plays", PlayViewSet)
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("theater_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "theatre"
