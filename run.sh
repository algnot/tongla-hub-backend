#!/bin/bash

echo "Waiting for MySQL to start..."
until mysqladmin ping -h"$DATABASE_HOST" -u"$DATABASE_USERNAME" -p"$DATABASE_PASSWORD" --port="$DATABASE_PORT" --silent; do
    sleep 2
done
echo "MySQL is up and running!"

if [ "$SERVICE_NAME" = "tongla-hub-server" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Starting Flask application..."
    exec python app.py
elif [ "$SERVICE_NAME" = "tongla-hub-consumer" ]; then
    echo "Starting Consumer application..."
    exec python app.py
elif [ "$SERVICE_NAME" = "tongla-hub-socket-server" ]; then
    echo "Starting Socket Server application..."
    exec python app.py
elif [ "$SERVICE_NAME" = "tongla-hub-cron" ]; then
    echo "Starting Cron Job Server application..."
    exec python app.py
else
    echo "Unknown service name: $SERVICE_NAME"
    exit 1
fi
