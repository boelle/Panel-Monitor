#!/bin/bash

if pgrep -f "python3 /home/pi/pool/poolweb.py" &>/dev/null; then
    echo "Web interface running"
    exit
else
    echo "starting web interface"
    stdbuf -oL sudo python3 /home/pi/pool/poolweb.py >/dev/null  &
fi
