#!/bin/bash

# Host and port where PostgreSQL is running
PG_HOST="localhost" # Change this to your PostgreSQL host if needed
PG_PORT=5432 # Default PostgreSQL port

# Time to wait before retrying
RETRY_INTERVAL=2  # Seconds

# Maximum number of retries (optional, you can remove the limit if desired)
MAX_RETRIES=30

# Check if PostgreSQL is up and running
is_postgres_up() {
    nc -z "$PG_HOST" "$PG_PORT" > /dev/null 2>&1
}

# Wait for PostgreSQL to be ready
echo "Checking PostgreSQL connection on ${PG_HOST}:${PG_PORT}..."

attempts=0
while ! is_postgres_up; do
    attempts=$((attempts+1))
    if [ "$attempts" -ge "$MAX_RETRIES" ]; then
        echo "Exceeded maximum number of retries. PostgreSQL is still not available."
        exit 1
    fi

    echo "PostgreSQL is not available yet. Waiting for ${RETRY_INTERVAL} seconds..."
    sleep "$RETRY_INTERVAL"
done

echo "PostgreSQL is up and running!"

# Start the Django server
echo "Starting Django server..."
python manage.py runserver
