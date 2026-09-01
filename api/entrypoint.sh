#!/bin/sh
# Container entrypoint: block until Postgres is reachable, optionally apply
# migrations, then hand off to the given command (gunicorn / uvicorn / alembic).
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

echo "entrypoint: waiting for postgres at ${DB_HOST}:${DB_PORT} ..."
i=0
until python -c "import socket,sys; s=socket.socket(); s.settimeout(2); s.connect((sys.argv[1], int(sys.argv[2])))" "$DB_HOST" "$DB_PORT" 2>/dev/null; do
    i=$((i + 1))
    if [ "$i" -ge 60 ]; then
        echo "entrypoint: postgres not reachable after 60s, giving up" >&2
        exit 1
    fi
    sleep 1
done
echo "entrypoint: postgres is up"

# Dev sets RUN_MIGRATIONS=1 to migrate on every start. In prod a dedicated
# one-shot 'migrate' service owns this instead, so the app containers don't race.
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    echo "entrypoint: alembic upgrade head ..."
    alembic upgrade head
fi

exec "$@"
