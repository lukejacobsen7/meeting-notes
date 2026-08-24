#!/bin/zsh
# record.sh [outfile] — capture a meeting to disk.
# Prefers an aggregate device that includes BlackHole (system audio = everyone else's voice).
# Falls back to the built-in mic, which works fine if you're on SPEAKERS, not headphones.
set -e
OUT="${1:-$HOME/Desktop/meeting-$(date +%Y%m%d-%H%M).wav}"
LIST=$(ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | sed -n '/AVFoundation audio devices/,$p')
pick() { echo "$LIST" | grep -i "$1" | head -1 | sed -E 's/.*\[([0-9]+)\].*/\1/'; }
IDX=$(pick "aggregate"); SRC="Aggregate (system audio + mic)"
[ -z "$IDX" ] && { IDX=$(pick "blackhole"); SRC="BlackHole (system audio only)"; }
[ -z "$IDX" ] && { IDX=$(pick "macbook pro microphone"); SRC="built-in mic — PUT THE CALL ON SPEAKERS"; }
[ -z "$IDX" ] && { echo "no audio device found"; exit 1; }
echo "recording from [$IDX] $SRC"
echo "  -> $OUT"
echo "  press q or ctrl-C to stop"
ffmpeg -hide_banner -loglevel warning -f avfoundation -i ":$IDX" -ar 16000 -ac 1 -c:a pcm_s16le "$OUT"
echo "saved: $OUT"
echo "now run:  ~/tools/meeting-notes/run.sh \"$OUT\" 4"
