#!/bin/bash

set -e

TIMESTAMP=$(date +"%Y%d%m%H%M%S")

alembic upgrade head

echo "Migration pulled successfully at $TIMESTAMP"
