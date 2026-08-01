#!/bin/bash
cd "$(dirname "$0")"
PORT=4757

if ! lsof -i ":$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  nohup node server.js > server.log 2>&1 &
  sleep 1
fi

open "http://localhost:$PORT/"
