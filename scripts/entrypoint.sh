#!/bin/sh
# Used from the Dockerfile, do not run manually

set -e

: "${PORT:=8000}"
: "${WORKERS:=4}"

exec "$@" --host 0.0.0.0 --port "$PORT" --workers "$WORKERS"
