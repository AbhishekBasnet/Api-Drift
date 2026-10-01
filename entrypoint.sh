#!/bin/sh
set -e

case "$1" in
  prod)
    exec fastapi run
    ;;
  dev)
    exec fastapi dev --host=0.0.0.0
    ;;
  *)
    echo "Unknown subcommand: $1"
    echo "Usage: entrypoint.sh [dev|prod]"
    exit 1
    ;;
esac
