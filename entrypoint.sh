#!/bin/sh
set -e
sleep 3
uv run alembic -c src/alembic.ini upgrade head
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8001