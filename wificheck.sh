#!/bin/bash

##################################################################
# Settings
# Which Interface do you want to check/fix
wlan='wlan0'
# Which address do you want to ping to see if the network interface is alive?
pingip='8.8.8.8'
##################################################################

echo -n "Current time : $(date) "
echo "Performing Network check for $wlan"
/bin/ping -c 1 -I $wlan $pingip > /dev/null 2> /dev/null
if [ $? -ge 1 ] ; then
    echo -n "Current time : $(date) "
    echo "Network connection down! Attempting reconnection."
    echo "Stopping wlan0"
    ip link set wlan0 down
    echo -n "Current time : $(date) "
    echo "Waiting for 5 Sec"
    sleep 5
    echo -n "Current time : $(date) "
    echo "Starting wlan0"
    ip link set wlan0 up
else
    echo -n "Current time : $(date) "
    echo "Network is Okay"
fi
