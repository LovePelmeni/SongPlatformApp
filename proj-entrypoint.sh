#!/bin/sh
echo "Making Migrations..."
python manage.py makemigrations
echo "Migrating..."
python manage.py migrate

echo "Running Tests."
pytest -q ./
python manage.py collectstatic --no-input
gunicorn VideoHost.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3
echo "Application Started."



