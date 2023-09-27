import os.path
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from app import settings


class Facility(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "facilities"

    def __str__(self):
        return self.name


def bus_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.info)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/buses/", filename)


class Bus(models.Model):
    info = models.CharField(max_length=255, null=True)
    num_seats = models.IntegerField()
    facilities = models.ManyToManyField(Facility, related_name="buses")
    image = models.ImageField(null=True, upload_to=bus_image_file_path)

    class Meta:
        verbose_name_plural = "buses"

    @property
    def is_mini(self):
        return self.num_seats <= 25

    def __str__(self):
        return str(self.info)


class Trip(models.Model):
    source = models.CharField(max_length=63)
    destination = models.CharField(max_length=63)
    departure = models.DateTimeField()
    bus = models.ForeignKey("Bus", on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"]),
            models.Index(fields=["departure"])
        ]

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.departure})"


class Ticket(models.Model):
    seat = models.IntegerField()
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["seat", "trip"], name="unique_ticket_seat_trip")
        ]
        ordering = ("seat",)

    def __str__(self):
        return f"{self.trip} - {self.seat}"

    @staticmethod
    def validate_seat(seat: int, num_seats: int, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise({
                "seat": f"seat must be in range [1, {num_seats}], not {seat}"
            })

    def clean(self):
        Ticket.validate_seat(self.seat, self.trip.bus.num_seats, ValidationError)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update,using,update_fields)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)
