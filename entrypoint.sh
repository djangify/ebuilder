#!/bin/bash
set -e

echo "=========================================="
echo "eBuilder Docker Entrypoint"
echo "=========================================="

INIT_MARKER="/app/db/.initialized"

if [ ! -f "$INIT_MARKER" ]; then
    echo "First boot detected"

    python manage.py migrate --noinput

    if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
        python manage.py create_admin_from_env
    fi

    python manage.py create_demo_product
    python manage.py collectstatic --noinput

    echo "$(date -Iseconds)" > "$INIT_MARKER"
else
    python manage.py migrate --noinput
fi

# ALWAYS ensure static files are present
python manage.py collectstatic --noinput

exec gunicorn ebuilder.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
