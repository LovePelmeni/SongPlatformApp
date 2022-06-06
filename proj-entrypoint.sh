#!/bin/sh
echo "Making Migrations..."
python manage.py makemigrations
echo "Migrating..."
python manage.py migrate

echo "Running Tests..."

pytest -q ./tests/services_integration_tests.py
pytest -q ./tests/test_models.py
pytest -q ./tests/test_views.py
pytest -q ./tests/test_subscriptions.py
pytest -q ./tests/test_albums.py
pytest -q ./tests/test_songs.py
pytest -q ./tests/test_customers.py

python manage.py collectstatic --no-input
gunicorn VideoHost.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3
echo "Application Started."
