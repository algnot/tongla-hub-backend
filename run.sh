#!/bin/bash

echo "Waiting for MySQL to start..."
until mysqladmin ping -h"$DATABASE_HOST" -u"$DATABASE_USERNAME" -p"$DATABASE_PASSWORD" --silent; do
    sleep 2
done
echo "MySQL is up and running!"

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Flask application..."
exec python -m flask run