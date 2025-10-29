# Procfile
web: python manage.py migrate && gunicorn config.wsgi:application --workers=2 --threads=4 --timeout=60 --preload

# Qué hace cada parte:

# Comando	Propósito
# python manage.py migrate	Aplica automáticamente las migraciones al iniciar el contenedor.
# gunicorn config.wsgi:application	Inicia el servidor de producción con Gunicorn (rápido y estable).
# --workers=2	Dos procesos de aplicación (ajustable según RAM/CPU).
# --threads=4	Cuatro hilos por proceso (buen balance para I/O).
# --timeout=60	Reinicia el worker si se cuelga más de 60 s.
# --preload	Carga el código una vez antes de crear los workers (ahorra RAM).