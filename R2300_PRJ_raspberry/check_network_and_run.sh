#!/bin/bash

TARGET="10.0.10.76"

while true; do
	ping -c 1 -W 1 $TARGET &> /dev/null
	if [ $? -eq 0 ]; then
		python3 ~/Desktop/R2300/http_handle_request_and_start.py
		python3 ~/Desktop/R2300/R2300_v1.5_raspberry.py
		exit 0
	else
		echo "retrying"
	fi
done