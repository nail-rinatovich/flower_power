#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Render mounts the persistent disk at runtime, not during the build/pre-deploy.
python manage.py migrate --noinput
exec gunicorn flower_power.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 --threads 4 --timeout 60 \
  --access-logfile - --error-logfile -
