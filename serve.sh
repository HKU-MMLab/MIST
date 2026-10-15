#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "MIST demo → http://127.0.0.1:${PORT:-8765}"
exec python3 -m http.server "${PORT:-8765}"
