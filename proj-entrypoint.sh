#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --username ${SUPERUSER_USERNAME} --password ${SUPERUSER_PASSWORD} --email ${SUPERUSER_EMAIL}

echo "Running Tests."
python manage.py test
python manage.py collectstatic --no-input
gunicorn VideoHost.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3
echo "Application Started."



