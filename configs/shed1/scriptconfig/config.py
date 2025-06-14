#!/usr/bin/python3
#-----------------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#     Pool Monitor System
#          config.py
#
# This is the configuration file. Use it to specific
# parameters unique to your system. If the Pushover and
# Thingspeak Keys are not specified then that functionality
# will not be available.
#
# Additional details of this project here:
# http://bit.ly/pizeropool
#
# Visit my Raspberry Pi Blog for other awesome content:
# https://www.raspberrypi-spy.co.uk/
#
# Modified by Bo Herrmannsen to control a electrical heating panel
#
#-----------------------------------------------------------------

# Set temp scale to
# C for Celcius/Centigrade or
# F for Fahrenheit
TEMPUNIT='C'

#Sensor id
id1='28-0517c09bb5ff'
id2='28-00000bc197ea'

# Set the number of seconds that pass before the relay is updated
LOOPSENDDATA=30

# Default username and password hash
# Use hashgenerator.py in utils to create hash for your password
USERNAME='admin'
USERHASH='fbf1e49dd4dcff041ac1df52d5f9ba5726bf4d8448d4a6098a3340df424e58e4'

# Flask needs a secret key or phrase to handle login cookie
FLASKSECRET='7e8031df78fd55cba971df8d9f5740be'

#MQTT broker info
MQTTUSER='test'
MQTTPASS='test'
MQTTHOST='192.168.0.9'
