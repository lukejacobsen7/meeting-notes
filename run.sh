#!/bin/zsh
# run.sh <audiofile> [speakers] — who-said-what transcript, fully offline.
cd "$(dirname "$0")"
. .venv/bin/activate
exec python3 notes.py "$1" --speakers "${2:-4}" "${@:3}"
