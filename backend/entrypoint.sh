#!/bin/sh
set -eu

if [ -n "${SQLITE_PATH:-}" ]; then
  mkdir -p "$(dirname "${SQLITE_PATH}")"
fi

poetry run python manage.py migrate --noinput

exec poetry run gunicorn \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile - \
  config.wsgi:application
