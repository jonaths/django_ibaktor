from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class Room(models.Model):

    class RoomType(models.TextChoices):
        SINGLE = "single", "Single"
        DOUBLE = "double", "Double"
        SUITE = "suite", "Suite"

    class RoomStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        MAINTENANCE = "maintenance", "Maintenance"

    number = models.CharField(max_length=10, unique=True, help_text="Número visible de habitación (ej. 101)")
    floor = models.IntegerField(null=True, blank=True)
    room_type = models.CharField(max_length=10, choices=RoomType.choices, default=RoomType.SINGLE)
    capacity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio base por noche")
    status = models.CharField(max_length=12, choices=RoomStatus.choices, default=RoomStatus.AVAILABLE)

    class Meta:
        ordering = ["number"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["room_type"]),
        ]

    def __str__(self) -> str:
        return f"Room {self.number} ({self.get_room_type_display()})"

class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        CHECKED_IN = "checked_in", "Checked in"
        CHECKED_OUT = "checked_out", "Checked out"
        CANCELLED = "cancelled", "Cancelled"

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    guest_name = models.CharField(max_length=120)
    guests_count = models.PositiveIntegerField(default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=12, choices=BookingStatus.choices, default=BookingStatus.RESERVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-check_in", "-created_at"]
        indexes = [
            models.Index(fields=["room", "check_in", "check_out"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.pk or 'new'} — Room {self.room.number} — {self.guest_name}"