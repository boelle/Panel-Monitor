#!/bin/bash

if pgrep -f "python3 /home/pi/pool/poolmain.py" &>/dev/null; then
    echo "Main script running"
    exit
else
    echo "starting main script"
    stdbuf -oL sudo python3 /home/pi/pool/poolmain.py >/dev/null  &
fi
