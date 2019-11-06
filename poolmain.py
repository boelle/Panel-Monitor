#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#     Pool Monitor System
#          poolmain.py
#
# This is the main script.
#
# It provides a loop and checks a schedule to determine
# if the pump should be on or off when in "auto" mode.
#
# Author : Matt Hawkins
# Date   : 06/08/2018
#
# Additional details of this project here:
# http://bit.ly/pizeropool
#
# Visit my Raspberry Pi Blog for other awesome content:
# https://www.raspberrypi-spy.co.uk/
#
#-----------------------------------------------------------
import time
import logging
import config as c
import poollib as p

logFormat='%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat,filename='/home/pi/pool/logs/main.log',level=logging.DEBUG)
logging.info('Main start')

# Check current saved status and create pickle files
# if they don't already exist
p.checkStatus()
p.checkSchedule()

# Get the IDs of the DS18B20 temp sensors
mySensorIDs=p.getSensorIDs()

# Set number of seconds to wait between loops
loopDelay=c.LOOPDELAY
# Set number of loops to wait before sending data to Thingspeak
loopSendData=c.LOOPSENDDATA

loopCounter=0

# Send Pushover notification on boot with IP
p.sendPushover(c.PUSHOVERURL,c.PUSHOVERUSR,c.PUSHOVERKEY,'50000')

if __name__ == '__main__':

  while True:

    # Read current schedule, pump status and mode
    # as it may have been changed by web interface since last loop
    myHours=p.getSchedule()
    myPumpMode,myPumpStatus,booststart=p.getStatus()

    # Deal with pump based on current mode
    myPumpStatus=p.pumpUpdate(myPumpMode)

    # Read temperatures in C or F and send to 
    # Thingspeak every 5 loops
    loopCounter+=1
    if loopCounter==loopSendData:
      temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
      p.sendThingspeak(c.THINGSPEAKURL,c.THINGSPEAKKEY,'field1','field2',temp1,temp2)
      loopCounter=0

    # Wait before doing it all again
    time.sleep(loopDelay)
