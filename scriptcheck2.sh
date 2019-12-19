#!/bin/bash

if pgrep -f "python3 /home/pi/pool/poolweb.py" &>/dev/null; then
    echo -n "Current time : $(date) "
    echo "Web interface running"
    exit
else
    echo -n "Current time : $(date) "
    echo "starting web interface"
    stdbuf -oL sudo python3 /home/pi/pool/poolweb.py >/dev/null  &
fi
