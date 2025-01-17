#!/bin/bash

set -e

TIMESTAMP=$(date +"%Y%d%m%H%M%S")

alembic revision --autogenerate -m "migrate-$TIMESTAMP"
alembic upgrade head

echo "Migration applied successfully at $TIMESTAMP"
