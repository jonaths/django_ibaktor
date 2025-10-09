from datetime import date
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Room, Booking


class BookingService:
    """
    Servicio de dominio para gestionar disponibilidad y reservas de un Room.

    Convención de intervalos: [check_in, check_out)
    - Es decir, la noche de check_out NO se incluye.
    - Back-to-back es válido: si una reserva termina el 1/oct, una nueva que
      inicia el 1/oct NO solapa.
    """

    ACTIVE_STATUSES = (
        Booking.BookingStatus.RESERVED,
        Booking.BookingStatus.CHECKED_IN,
    )

    def __init__(self, room: Room):
        self.room = room

    def _validate_range(self, check_in: date, check_out: date) -> None:
        if not isinstance(check_in, date) or not isinstance(check_out, date):
            raise ValidationError("check_in y check_out deben ser fechas (date).")
        if check_in >= check_out:
            raise ValidationError("`check_in` debe ser estrictamente menor que `check_out`.")

    def is_available(self, check_in: date, check_out: date) -> bool:
        """
        Devuelve True si la habitación está disponible en [check_in, check_out),
        considerando:
          - Sin reservas activas solapadas.
          - La habitación NO esté en mantenimiento.
        """
        self._validate_range(check_in, check_out)

        # No disponible si la habitación está en mantenimiento
        if self.room.status == Room.RoomStatus.MAINTENANCE:
            return False

        # Solapamiento si: A < D y C < B
        overlapping = Booking.objects.filter(
            room=self.room,
            status__in=self.ACTIVE_STATUSES,
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).exists()

        return not overlapping

    @transaction.atomic
    def reserve(
        self,
        check_in: date,
        check_out: date,
        guest_name: str,
        guests_count: int = 1,
        status: Optional[str] = None,
    ) -> Booking:
        """
        Crea una reserva si hay disponibilidad. Lanza ValidationError si no.
        - `status` por defecto = RESERVED.
        - Valida capacidad mediante Booking.full_clean() (si lo definiste).
        """
        self._validate_range(check_in, check_out)

        # Checar disponibilidad previa
        if not self.is_available(check_in, check_out):
            raise ValidationError("La habitación no está disponible en ese periodo.")

        if status is None:
            status = Booking.BookingStatus.RESERVED

        booking = Booking(
            room=self.room,
            guest_name=guest_name,
            guests_count=guests_count,
            check_in=check_in,
            check_out=check_out,
            status=status,
        )

        # Ejecuta validaciones del modelo (capacidad, mantenimiento, etc.)
        booking.full_clean()
        booking.save()
        return booking