#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn ebuilder.wsgi:application --bind 0.0.0.0:8000 --workers 3