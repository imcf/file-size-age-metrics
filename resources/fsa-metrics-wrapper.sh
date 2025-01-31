#!/bin/bash

# FIXME FIXME FIXME
echo "ERROR: needs refactorig!"
exit 1

export FSA_DIR=/export01/postgresql/backup/
export FSA_PATTERN="**"

RUNNER=file-size-age-metrics.py

# shellcheck disable=SC2164
cd "$(dirname "$0")"

if ! pgrep -f "$RUNNER" > /dev/null; then
    echo "WARNING: No metrics process found, starting a new instance!"
    ( python3 $RUNNER ) &
fi
