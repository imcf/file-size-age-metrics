#!/bin/bash

VENV_PATH="$HOME/.virtualenvs/fsa-metrics"

export FSA_CONFIG="$VENV_PATH/fsa-metrics.yaml"

RUNNER="$VENV_PATH/bin/fsa-metrics"

IS_IT_RUNNING="$(pgrep -f "$RUNNER")"
# echo "Is it running? $IS_IT_RUNNING"
if [ -z "$IS_IT_RUNNING" ]; then
    echo "WARNING: No metrics process found, starting a new instance!"
    "$RUNNER" &
# else
#     echo "Found process: $IS_IT_RUNNING - not starting another instance."
fi
