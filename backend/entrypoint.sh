#!/bin/sh
# Run migrations on every start (idempotent), then hand off to whatever
# command the image (gunicorn, prod) or the compose override (runserver, dev)
# provides. Keeping migrate here means it happens in both modes, exactly once.
set -e
python manage.py migrate
exec "$@"
