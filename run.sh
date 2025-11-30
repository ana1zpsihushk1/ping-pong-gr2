#!/bin/bash

> session.log
TO_SERVER="to_server.fifo"
TO_CLIENT="to_client.fifo"

rm -f $TO_SERVER $TO_CLIENT

mkfifo $TO_SERVER
mkfifo $TO_CLIENT

echo "[BASH] FIFO files were created."

python3 server.py &
SERVER_PID=$!

echo "[BASH] Server is working. PID=$SERVER_PID"
echo "[BASH] Client is launching..."
echo

python3 client.py

echo
echo "[BASH] Client is stopping."
echo "[BASH] Killing all processes..."

kill $SERVER_PID
sleep 0.2

echo "[BASH] FIFO files are clearing..."
rm -f $TO_SERVER $TO_CLIENT

echo "[BASH] Ready."
