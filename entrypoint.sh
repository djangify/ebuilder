#!/bin/bash
set -e

echo "=========================================="
echo "eBuilder Docker Entrypoint"
echo "=========================================="

INIT_MARKER="/app/db/.initialized"

# First boot initialization
if [ ! -f "$INIT_MARKER" ]; then
    echo "First boot detected - initializing..."
    
    python manage.py migrate --noinput

    # Create admin user from environment variables
    if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
        echo "Creating admin user..."
        python manage.py create_admin_from_env
    fi

    touch "$INIT_MARKER"
    echo "$(date -Iseconds)" > "$INIT_MARKER"
    echo "First boot initialization complete!"
else
    echo "Existing installation detected"
    python manage.py migrate --noinput
fi

echo "Starting eBuilder on port 8000..."

exec gunicorn ebuilder.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3