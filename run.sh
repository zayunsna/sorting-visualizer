#!/bin/sh
# Run from any working directory.
cd "$(dirname "$0")" || exit 1
exec python3 sort_visualizer.py "$@"
