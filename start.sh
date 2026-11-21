#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Free services have no Shell: initialize the runtime database on every start.
python manage.py migrate --noinput
python manage.py bootstrap_admin
if [ "${SEED_DEMO_DATA:-0}" = "1" ]; then
  python manage.py seed_shop
fi
exec gunicorn flower_power.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 --threads 4 --timeout 60 \
  --access-logfile - --error-logfile -
