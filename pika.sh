#!/bin/bash
# pika.sh — PKA startup script
# Bootstraps Libby's database, then starts the inbox watchdog.

cd "$(dirname "$0")"

python3 .scripts/libby_init.py
python3 .scripts/libby_watch.py &
