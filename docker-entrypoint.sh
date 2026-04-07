#!/bin/sh
set -e

echo "→ Running migrations..."
python manage.py migrate --noinput

echo "→ Seeding database (skipped if already seeded)..."
python manage.py seed

echo "→ Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
