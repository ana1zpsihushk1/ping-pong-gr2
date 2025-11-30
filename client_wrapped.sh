#!/bin/bash

echo "Client programm is loading..."

echo "Waiting for server..."
while [ ! -p to_client.fifo ] || [ ! -p to_server.fifo ]; do
	sleep 1
done

exec 5<> to_server.fifo
exec 6<> to_client.fifo

client() {
	python3 client.py 2>&1 | while IFS= read -r line; do
		echo "[ CLIENT ] $line"
	done
}

client

exec 5>&-
exec 6>&-

echo "Client is stopped working"
