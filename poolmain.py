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
# Modified by Bo Herrmannsen to control a electrical heating panel
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
p.checkTarget()
p.checkTarget2()
p.checkTarget3()
p.checkTarget4()
p.checkTargetON()
p.checkTargetOFF()

# Get the IDs of the DS18B20 temp sensors
mySensorIDs=p.getSensorIDs()
# Set number of seconds to wait between loops
loopDelay=c.LOOPDELAY
# Set number of loops to wait before updating relay
loopSendData=c.LOOPSENDDATA

loopCounter=0

if __name__ == '__main__':

  while True:

    # Read temperatures in C or F and send to
    # Emoncms every 1 loops

    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
    myPumpMode,myPumpStatus,booststart=p.getStatus()
    p.sendEmoncms(c.domain,c.domain1,c.apikey,c.emoncmspath,c.nodeid,temp1,temp2,myPumpStatus,myPumpMode)

    # Update relay every 3 loops
    loopCounter+=1
    if loopCounter==loopSendData:

      # Read current schedule, pump status and mode
      # as it may have been changed by web interface since last loop
      myHours=p.getSchedule()
      target=p.getTarget()
      target2=p.getTarget2()
      target3=p.getTarget3()
      target4=p.getTarget4()
      targetON=p.getTargetON()
      targetOFF=p.getTargetOFF()
      myPumpMode,myPumpStatus,booststart=p.getStatus()

      # Deal with pump based on current mode
      myPumpStatus=p.pumpUpdate(myPumpMode)

      loopCounter=0

    # Wait before doing it all again
    time.sleep(loopDelay)
