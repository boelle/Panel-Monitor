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
id1='take a guess'
id2='take a guess'

# Set the number of seconds that pass before the relay is updated
LOOPSENDDATA=30

# Default username and password hash
# Use hashgenerator.py in utils to create hash for your password
USERNAME='admin'
USERHASH='c7f9e589934a99848f2dba75a70b49dca6149988730389671d730e9376701adf'

# Flask needs a secret key or phrase to handle login cookie
FLASKSECRET='7e8031df78fd55cba971df8d9f5740be'

#MQTT broker info
MQTTUSER='test'
MQTTPASS='test'
MQTTHOST='test'
HANAME='test'
