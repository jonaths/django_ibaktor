from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "room_type", "capacity", "base_price", "status", "floor")
    list_filter = ("room_type", "status", "floor")
    search_fields = ("number",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "guest_name", "check_in", "check_out", "status", "guests_count", "created_at")
    list_filter = ("status", "check_in", "check_out")
    search_fields = ("guest_name", "room__number")
    autocomplete_fields = ("room",)