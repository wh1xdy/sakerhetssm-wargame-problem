#!/bin/bash
set -e

# Ensure cron can read the file and start cron
echo "[+] Starting cron"
touch /etc/cron.d/ctf
chmod 0644 /etc/cron.d/ctf
service cron start

# Start nginx in the background
echo "[+] Starting nginx"
nginx

# Start Gunicorn in foreground (PID 1)
echo "[+] Starting gunicorn"
exec gunicorn --chdir /home/ctf/app \
    --worker-class eventlet -w 1 \
    server:app \
    -b unix:/tmp/ctf.sock
