#!/bin/bash

if pgrep -f "python3 /home/pi/pool/poolmain.py" &>/dev/null; then
    echo "it is already running"
    exit
else
    echo "starting"
    stdbuf -oL sudo python3 /home/pi/pool/poolmain.py >/dev/null  &
fi