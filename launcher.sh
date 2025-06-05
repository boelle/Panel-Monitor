#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script
activate() {
. /home/pi/ha_mqtt_discoverable/bin/activate
}
activate
python3 /home/pi/pool/poolmain.py &
