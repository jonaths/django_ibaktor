# hotel/views.py
# ==========================================================
# Este módulo contiene los controladores (views) de Django.
# Las "views" son funciones que reciben un HttpRequest y
# devuelven un HttpResponse. En este caso representan
# las pantallas del flujo básico de un sistema de reservas
# de hotel (buscar → reservar → confirmar).
# ==========================================================

from __future__ import annotations
from datetime import timedelta
from typing import Optional

# Importamos los módulos estándar de Django
from django import forms
from django.contrib import messages  # para mostrar avisos en la interfaz
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone  # para manejar fechas sin zonas horarias

# Importamos nuestros modelos y servicios del dominio
from .models import Booking, Room
from .services import BookingService


# ==========================================================
# 🧾 Formularios
# ==========================================================
# En Django, los formularios (Form) sirven para manejar datos
# de entrada del usuario: validarlos, convertirlos en tipos
# Python y generar los campos HTML correspondientes.
# ==========================================================

class AvailabilityForm(forms.Form):
    """
    Formulario para buscar habitaciones disponibles.
    Se usa en la página principal de disponibilidad.
    """
    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    room_type = forms.ChoiceField(
        choices=[("", "Cualquiera")] + list(Room.RoomType.choices),
        required=False,
    )
    guests_count = forms.IntegerField(min_value=1, initial=1)

    def clean(self):
        """
        Validación personalizada: la fecha de entrada
        debe ser menor que la fecha de salida.
        """
        cleaned = super().clean()
        ci = cleaned.get("check_in")
        co = cleaned.get("check_out")
        if ci and co and ci >= co:
            raise forms.ValidationError("La fecha de entrada debe ser menor a la de salida.")
        return cleaned


class BookingForm(forms.Form):
    """
    Formulario para crear una reserva de habitación.
    Se usa en la vista de booking_create.
    """
    room_id = forms.IntegerField(widget=forms.HiddenInput)
    guest_name = forms.CharField(max_length=120)
    guests_count = forms.IntegerField(min_value=1, initial=1)
    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        """
        Misma validación de rango de fechas.
        """
        cleaned = super().clean()
        ci = cleaned.get("check_in")
        co = cleaned.get("check_out")
        if ci and co and ci >= co:
            raise forms.ValidationError("La fecha de entrada debe ser menor a la de salida.")
        return cleaned


# ==========================================================
# 🧭 Controladores (Views)
# ==========================================================
# Estas funciones definen la lógica de cada pantalla.
# - room_availability: busca habitaciones disponibles.
# - booking_create: crea una reserva concreta.
# - booking_success: muestra confirmación final.
# ==========================================================

def room_availability(request: HttpRequest) -> HttpResponse:
    """
    Página principal de búsqueda de disponibilidad.
    - GET: muestra el formulario con fechas por defecto (hoy, hoy+3).
    - POST: procesa el formulario y muestra habitaciones disponibles.

    ⚠️ NOTA DIDÁCTICA:
    En un diseño profesional, la lógica de disponibilidad debería
    delegarse al BookingService (is_available), pero aquí se deja
    explícita para fines educativos.
    """
    today = timezone.localdate()  # obtiene la fecha actual (sin hora)
    initial = {
        "check_in": today,
        "check_out": today + timedelta(days=3),
        "guests_count": 1,
    }

    if request.method == "POST":
        # Si el usuario envía el formulario (POST)
        form = AvailabilityForm(request.POST)
        available_rooms = []
        if form.is_valid():
            # Extraemos los datos limpios del formulario
            check_in = form.cleaned_data["check_in"]
            check_out = form.cleaned_data["check_out"]
            guests_count = form.cleaned_data["guests_count"]
            room_type = form.cleaned_data["room_type"]

            # 1. Filtramos habitaciones disponibles por capacidad y estado
            qs = Room.objects.exclude(status=Room.RoomStatus.MAINTENANCE).filter(capacity__gte=guests_count)
            if room_type:
                qs = qs.filter(room_type=room_type)

            # 2. Calculamos las habitaciones ocupadas en el rango dado
            busy_room_ids = Booking.objects.filter(
                status__in=[Booking.BookingStatus.RESERVED, Booking.BookingStatus.CHECKED_IN],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).values_list("room_id", flat=True)

            # 3. Excluimos las habitaciones ocupadas del conjunto base
            available_rooms = qs.exclude(id__in=busy_room_ids)

            # Si no hay resultados, mostramos un mensaje de advertencia
            if not available_rooms.exists():
                messages.info(request, "No hay habitaciones disponibles en ese rango con los filtros seleccionados.")

        # Renderizamos la plantilla con los resultados (o errores)
        context = {
            "form": form,
            "available_rooms": available_rooms,
            "results": True,
        }
        return render(request, "hotel/availability.html", context)

    # Si es un GET (primera carga), mostramos el formulario vacío con valores iniciales
    form = AvailabilityForm(initial=initial)
    return render(request, "hotel/availability.html", {"form": form, "results": False})


def booking_create(request: HttpRequest, room_id: int) -> HttpResponse:
    """
    Crea una reserva para una habitación específica.

    Flujo:
    - GET → muestra el formulario prellenado con la habitación seleccionada.
    - POST → valida el formulario y llama a BookingService.reserve().

    Si la reserva se crea con éxito, redirige a la pantalla de confirmación.
    """
    # Busca la habitación por su ID o devuelve un error 404 si no existe
    room = get_object_or_404(Room, pk=room_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            # Validamos que el ID de la habitación en el formulario
            # coincida con el que viene en la URL (seguridad básica)
            if form.cleaned_data["room_id"] != room.id:
                form.add_error(None, "La habitación del formulario no coincide con la URL.")
            else:
                # Extraemos los datos del formulario
                check_in = form.cleaned_data["check_in"]
                check_out = form.cleaned_data["check_out"]
                guest_name = form.cleaned_data["guest_name"]
                guests_count = form.cleaned_data["guests_count"]

                try:
                    # Intentamos crear la reserva usando el servicio
                    booking = BookingService(room).reserve(
                        check_in=check_in,
                        check_out=check_out,
                        guest_name=guest_name,
                        guests_count=guests_count,
                    )
                except ValidationError as e:
                    # Si hay error de negocio (no disponible, fechas inválidas, etc.)
                    form.add_error(None, e.message if hasattr(e, "message") else str(e))
                else:
                    # Si todo sale bien, mostramos un mensaje y redirigimos
                    messages.success(request, f"Reserva creada (# {booking.pk}) para la habitación {room.number}.")
                    return redirect(reverse("hotel:booking_success", kwargs={"booking_id": booking.pk}))

        # Si el formulario no es válido, se vuelve a mostrar con los errores
        return render(request, "hotel/booking_create.html", {"form": form, "room": room})

    # GET: inicializamos valores por defecto en el formulario
    today = timezone.localdate()
    initial = {
        "room_id": room.id,
        "check_in": today,
        "check_out": today + timedelta(days=2),
        "guests_count": 1,
    }
    form = BookingForm(initial=initial)
    return render(request, "hotel/booking_create.html", {"form": form, "room": room})


def booking_success(request: HttpRequest, booking_id: int) -> HttpResponse:
    """
    Pantalla final de confirmación de reserva.

    Muestra la información completa de la reserva recién creada.
    """
    # select_related("room") evita múltiples consultas a la base de datos.
    booking = get_object_or_404(Booking.objects.select_related("room"), pk=booking_id)
    return render(request, "hotel/booking_success.html", {"booking": booking})
