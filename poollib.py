#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#     Pool Monitor System
#          poollib.py
#
# This is a supporting set of functions that are used
# by the main script (poolmain.py) and the web front-end (poolweb.py).
#
# It serves a status page and allows users to set the
# pump mode and edit the schedule.
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

import os
import time
import datetime
import pickle
import requests
from gpiozero import Energenie

# Create pump object using gpiozero library
pump = Energenie(1)

def sendPushover(url,user,token,port):
  if url=='' or user=='' or token=='':
    return

  try:
    ip = requests.get('https://api.ipify.org',timeout=30)
    myurl="http://"+ip.text+":"+port
  except:
    myurl="http://0.0.0.0"

  title="Pool monitor has rebooted"
  message="Your Pool Monitor has just rebooted"
  payload = {
        "token": token,      # Pushover app token
        "user":  user,       # Pushover user token
        "html": "1",         # 1 for HTML, 0 to disable
        "title": title,      # Title of message
        "message": message,  # Content of message (HTML if required)
        "url": myurl,        # Link to include in message
        "url_title": myurl,  # Text for link
        "sound": "tugboat"   # Define sound played on receiving device
      }
  try:
    r = requests.post(url,data=payload,timeout=5)
    if r.status_code==200:
      print("Sent notification to pushover")
    else:
      print("Error sending notification to pushover (status code:"+str(r.status_code)+")")
  except:
    print("Error sending notification to pushover")

def sendThingspeak(url,key,field1,field2,temp1,temp2):
  if url=='' or key=='':
    return

  # Send event to internet site
  payload = {'key' : key,'field1' : temp1,'field2' : temp2}
  try:
    r = requests.post(url,data=payload,timeout=5)
    if r.status_code==200:
      print("Sent data to Thingspeak")
    else:
      print("Error sending data to Thingspeak (status code:"+str(r.status_code)+")")
  except:
    print("Error sending data to Thingspeak")

def saveStatus(mode,status,booststart):
  try:
    pickle.dump( [mode,status,booststart], open( "/home/pi/pool/status.p", "wb" ) )
  except:
    print("Problem saving status")

def getStatus():
  mode,status,booststart=pickle.load(open( "/home/pi/pool/status.p", "rb" ))
  return mode,status,booststart

def saveSchedule(hours):
  try:
    pickle.dump( hours, open( "/home/pi/pool/schedule.p", "wb" ) )
  except:
    print("Problem saving schedule")

def getSchedule():
  hours=pickle.load(open( "/home/pi/pool/schedule.p", "rb" ))
  return hours

def checkStatus():
  if not os.path.isfile('/home/pi/pool/status.p'):
    print("No status.p file found")
    saveStatus('off',False,0)
  else:
    print("Existing status.p file found")

def checkSchedule():
  if not os.path.isfile('/home/pi/pool/schedule.p'):
    print("No schedule.p file found")
    saveSchedule(['7','8'])
  else:
    print("Existing schedule.p file found")

def readTemps(sensorID,tempunit='C'):
    read1=getTemp(sensorID[0])/float(1000)
    read2=getTemp(sensorID[1])/float(1000)
    
    if tempunit.upper()=='F':
      # Convert to Fahrenheit if unit is F
      read1=(read1*1.8)+32
      read2=(read2*1.8)+32

    t1='{:.1f}'.format(read1)
    t2='{:.1f}'.format(read2)
    return t1,t2

def getTemp(id):
  try:
    mytemp = ''
    filename = 'w1_slave'
    f = open('/sys/bus/w1/devices/' + id + '/' + filename, 'r')
    line = f.readline() # read 1st line
    crc = line.rsplit(' ',1)
    crc = crc[1].replace('\n', '')
    if crc=='YES':
      line = f.readline() # read 2nd line
      mytemp = line.rsplit('t=',1)
    else:
      mytemp = 99999
    f.close()

    return int(mytemp[1])

  except:
    return 99999

def getSensorIDs():
  sensorIDs=[]

  try:
    for item in os.walk('/sys/bus/w1/devices/'):
      dirs=item[1]
      for dir in dirs:
        if dir[:3]=='28-':
          sensorIDs.append(dir)
  except:
    sensorIDs=['28-01','28-02']
  if len(sensorIDs)==0:
    sensorIDs=['1','2']
  return sensorIDs

def pumpUpdate(mode):

  prevPumpMode,prevPumpStatus,booststart=getStatus()
  hours=getSchedule()

  if mode=='on':
    pump.on()
    status=True
  elif mode=='off':
    pump.off()
    status=False
  elif mode=='boost':
    if prevPumpMode=='boost' and time.time()-booststart>3600:
      pump.off()
      status=False
      mode='auto'
    else:
      pump.on()
      status=True
  elif mode=='auto':
    now = datetime.datetime.now()
    if str(now.hour) in hours:
      pump.on()
      status=True
    else:
      pump.off()
      status=False
  else:
    pump.off()
    status=False

  print("Current pump status : "+str(status))
  print("Current pump mode : "+mode)

  # If there has been a change in state save status
  if status!=prevPumpStatus or mode!=prevPumpMode:
    booststart=time.time()
    saveStatus(mode,status,booststart)
  else:
    print("No change in status so don't save")

  return status
