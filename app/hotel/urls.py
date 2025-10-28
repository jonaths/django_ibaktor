# hotel/urls.py
# ----------------------------------------
# Este archivo define las rutas (URLs) específicas
# para la aplicación "hotel". Cada ruta asocia una
# dirección en el navegador con una función (vista)
# que se ejecutará cuando se visite esa dirección.
# ----------------------------------------

# Importamos path para definir rutas, y nuestras vistas.
from django.urls import path
from . import views

# app_name se usa para "namespacing" en Django.
# Permite referirnos a las rutas de esta app usando
# el prefijo 'hotel:' en los templates o en redirect().
# Ejemplo: {% url 'hotel:availability' %}
app_name = "hotel"

# urlpatterns es una lista de rutas.
# Django las evalúa de arriba hacia abajo.
urlpatterns = [
    # Ruta principal (raíz del sitio)
    # Muestra el formulario de búsqueda de habitaciones disponibles.
    # http://127.0.0.1:8000/
    path("", views.room_availability, name="availability"),

    # Ruta para crear una reserva de una habitación específica.
    # <int:room_id> captura un número en la URL y lo pasa como argumento
    # a la función 'booking_create(request, room_id)'.
    # Ejemplo: http://127.0.0.1:8000/booking/5/
    path("booking/<int:room_id>/", views.booking_create, name="booking_create"),

    # Ruta para mostrar la página de confirmación de una reserva.
    # <int:booking_id> indica el identificador de la reserva creada.
    # Ejemplo: http://127.0.0.1:8000/booking/success/12/
    path("booking/success/<int:booking_id>/", views.booking_success, name="booking_success"),
]
