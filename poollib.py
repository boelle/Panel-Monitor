#!/usr/bin/python3
#---------------------------------------------------------------------
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
# Modified by Bo Herrmannsen to control a electrical heating panel
#
#---------------------------------------------------------------------

import os
import time
import datetime
import pickle
import requests
import config as c
import wiringpi
import sys, string
import http.client
import socket

# wiringpi numbers

wiringpi.wiringPiSetup()
wiringpi.pinMode(0, 1)  # sets pin 0 to output (GPIO 17, Actual hardware pin number is 11) (Relay)
wiringpi.pinMode(2, 1)  # sets pin 2 to output (GPIO 27, Actual hardware pin number is 13) (Internet connection LED)
wiringpi.pinMode(25, 1)  # sets pin 25 to output (GPIO 26, Actual hardware pin number is 37) (Spare LED)
wiringpi.pinMode(3, 0)  # sets pin 3 to input (GPIO 22, Actual hardware pin number is 15) (latching button)

def internet_connected(host='8.8.8.8', port=53):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(20)
        socket.socket(socket.AF_INET,
                      socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))

    return False

def sendEmoncms(domain,domain1,apikey,emoncmspath,nodeid,temp1,temp2,status,mode):

    try:
        hours=getSchedule()
        now = datetime.datetime.now()
        if status==True:
          relay=1
        if status==False:
          relay=0
        if mode=='boost':
          targetnew=target_new()
        if mode=='auto':
          targetnew=target_new2()
        if str(now.hour) in hours and mode=='auto':
          targetnew=target_new1()        
        cpunew=cpu()
        uptimenew=uptime()

        seq = (temp1, temp2, targetnew, relay, cpu(), uptime())
        str_join = ",".join(str(x) for x in seq)
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Preparing Data for local server')
        conn = http.client.HTTPConnection(domain)
        
        conarg1 = ('/', emoncmspath, '/input/post?node=', str(nodeid), '&csv=', str_join, '&apikey=', apikey)
        conarg = "".join(str(x) for x in conarg1)

        conn.request("GET", conarg)
        
        response = conn.getresponse()
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Response from local server:', end=' ')
        print(response.read())
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Data sent to local server')
        
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Preparing Data for hosted server')
        conn = http.client.HTTPConnection(domain1)
        
        conarg1 = ('/', emoncmspath, '/input/post?node=', str(nodeid), '&csv=', str_join, '&apikey=', apikey)
        conarg = "".join(str(x) for x in conarg1)

        conn.request("GET", conarg)
        
        response = conn.getresponse()
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Response from hosted server:', end=' ')
        print(response.read())
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Data sent to hosted server')
                        
    except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def uptime():

    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = (((uptime_seconds/60)/60)/24)
            print(time.asctime( time.localtime(time.time()) ), end=' ')
            print(' Uptime since last reboot: ', end=' ')
            print (uptime_string)

            return uptime_string

    except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))   

def cpu():

    try:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Getting CPU Temp')
        temp = os.popen("vcgencmd measure_temp").readline()
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' Got CPU Temp')

        return (temp.replace("temp=","").replace("'C\n",""))

    except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def saveStatus(mode,status,booststart):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving status file')
    pickle.dump( [mode,status,booststart], open( "/home/pi/pool/status.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getStatus():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting status file')
    mode,status,booststart=pickle.load(open( "/home/pi/pool/status.p", "rb" ))
    return mode,status,booststart
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def saveSchedule(hours):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving schedule file')
    pickle.dump( hours, open( "/home/pi/pool/schedule.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def saveTarget(target):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving target file')
    pickle.dump( target, open( "/home/pi/pool/target.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def saveTarget2(target2):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving target2 file')
    pickle.dump( target2, open( "/home/pi/pool/boost.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def saveTarget3(target3):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving target3 file')
    pickle.dump( target3, open( "/home/pi/pool/cpu.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))
        
def saveTarget4(target4):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Saving target4 file')
    pickle.dump( target4, open( "/home/pi/pool/night.p", "wb" ) )
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))        

def getSchedule():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting schedule file')
    hours=pickle.load(open( "/home/pi/pool/schedule.p", "rb" ))
    return hours
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getTarget():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting target file')
    target=pickle.load(open( "/home/pi/pool/target.p", "rb" ))
    return target
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getTarget2():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting target2 file')
    target2=pickle.load(open( "/home/pi/pool/boost.p", "rb" ))
    return target2
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getTarget3():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting target3 file')
    target3=pickle.load(open( "/home/pi/pool/cpu.p", "rb" ))
    return target3
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getTarget4():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting target4 file')
    target4=pickle.load(open( "/home/pi/pool/night.p", "rb" ))
    return target4
    print(time.asctime( time.localtime(time.time()) ), end=' ')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))
        
def checkStatus():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking status file')

    if not os.path.isfile('/home/pi/pool/status.p'):
      print("No status.p file found")
      saveStatus('off',False,0)
    else:
      print("Existing status.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def checkSchedule():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking schedule file')

    if not os.path.isfile('/home/pi/pool/schedule.p'):
      print("No schedule.p file found")
      saveSchedule(['7','8'])
    else:
      print("Existing schedule.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def checkTarget():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking target file')

    if not os.path.isfile('/home/pi/pool/target.p'):
      print("No target.p file found")
      saveTarget(['20'])
    else:
      print("Existing target.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def checkTarget2():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking target2 file')

    if not os.path.isfile('/home/pi/pool/boost.p'):
      print("No boost.p file found")
      saveTarget2(['25'])
    else:
      print("Existing boost.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def checkTarget3():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking target3 file')

    if not os.path.isfile('/home/pi/pool/cpu.p'):
      print("No cpu.p file found")
      saveTarget3(['50'])
    else:
      print("Existing cpu.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def checkTarget4():
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Checking target4 file')

    if not os.path.isfile('/home/pi/pool/night.p'):
      print("No night.p file found")
      saveTarget4(['15'])
    else:
      print("Existing night.p file found")

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))        
        
def readTemps(sensorID,tempunit='C'):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Reading Temperatures')
    read1=getTemp(sensorID[0])/float(1000)
    read2 = getTemp(sensorID[1]) / float(1000)

    if tempunit.upper()=='F':
      print(time.asctime( time.localtime(time.time()) ), end=' ')
      print(' Converting to Fahrenheit')

      # Convert to Fahrenheit if unit is F
      read1=(read1*1.8)+32
      read2=(read2*1.8)+32

    t1='{:.1f}'.format(read1)
    t2='{:.1f}'.format(read2)

    return t1,t2
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Got Temperatures')

  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))

def getTemp(id):
  try:
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Getting Temperature')
    mytemp = ''
    filename = 'w1_slave'
    f = open('/sys/bus/w1/devices/' + id + '/' + filename, 'r')
    line = f.readline() # read 1st line
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Got Temperature - Now checking crc')
    crc = line.rsplit(' ',1)
    crc = crc[1].replace('\n', '')
    if crc=='YES':
      print(time.asctime( time.localtime(time.time()) ), end=' ')
      print(' Crc ok')
      line = f.readline() # read 2nd line
      mytemp = line.rsplit('t=',1)
    else:
      print(time.asctime( time.localtime(time.time()) ), end=' ')
      print(' Crc failed')
      mytemp = 99999
    f.close()

    return int(mytemp[1])
    print(time.asctime( time.localtime(time.time()) ), end=' ')
    print(' Got Temperature')


  except Exception as ex:
        print(time.asctime( time.localtime(time.time()) ), end=' ')
        print(' This error occurred: ' + str(ex))
        return 99999

def getSensorIDs():
  id1=c.id1
  id2=c.id2

  sensorIDs=[]

  sensorIDs.append(id1)
  sensorIDs.append(id2)

  return sensorIDs

def pumpUpdate(mode):

  prevPumpMode,prevPumpStatus,booststart=getStatus()
  hours=getSchedule()
  t1,t2=readTemps(getSensorIDs(),c.TEMPUNIT)
  cpu1=cpu()
  target=getTarget()
  for i in range(0, len(target)):
      target_new=(target[i])
  target2=getTarget2()
  for i in range(0, len(target2)):
      target2_new=(target2[i])
  target3=getTarget3()
  for i in range(0, len(target3)):
      target3_new=(target3[i])
  target4=getTarget4()
  for i in range(0, len(target4)):
      target4_new=(target4[i])    

  if internet_connected():
    print(time.asctime( time.localtime(time.time()) ), end=' '),
    print (" We have an internet connection? " + str(internet_connected()))
    wiringpi.digitalWrite(2, 0) # sets port 2 to OFF
  else:
    print (" Check internet Connection")
    wiringpi.digitalWrite(2, 1) # sets port 2 to ON

  if mode=='on':
    if t1 < target_new and cpu1 < target3_new:
      wiringpi.digitalWrite(0, 1) # sets port 0 to ON
      status=True
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target: "+target_new)
      print ("CPU Cap: "+target3_new)
    else:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target: "+target_new)
      print ("CPU Cap: "+target3_new)
  elif mode=='off':
    wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
    status=False
  elif mode=='boost':
    wiringpi.digitalWrite(25, 1) # sets port 25 to ON (spare LED)
    if prevPumpMode=='boost' and time.time()-booststart>900:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      mode='auto'
      wiringpi.digitalWrite(25, 0) # sets port 25 to OFF (spare LED)
    else:
      if t1 < target2_new and cpu1 < target3_new:
        wiringpi.digitalWrite(0, 1) # sets port 0 to ON
        status=True
        print ("Current Temperature: "+t1)
        print ("CPU Temperature: "+cpu1)
        print ("Target(boost): "+target2_new)
        print ("CPU Cap: "+target3_new)
      else:
        wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
        status=False
        print ("Current Temperature: "+t1)
        print ("CPU Temperature: "+cpu1)
        print ("Target(boost): "+target2_new)
        print ("CPU Cap: "+target3_new)
  elif mode=='auto':
    now = datetime.datetime.now()
    if str(now.hour) in hours and t1 < target_new and cpu1 < target3_new:
      wiringpi.digitalWrite(0, 1) # sets port 0 to ON
      status=True
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Day): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) in hours and t1 > target_new and cpu1 < target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Day): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) in hours and t1 < target_new and cpu1 > target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Day): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) in hours and t1 > target_new and cpu1 > target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Day): "+target_new)
      print ("CPU Cap: "+target3_new)

    if str(now.hour) not in hours and t1 < target4_new and cpu1 < target3_new:
      wiringpi.digitalWrite(0, 1) # sets port 0 to ON
      status=True
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Night): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) not in hours and t1 > target4_new and cpu1 < target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Night): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) not in hours and t1 < target4_new and cpu1 > target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Night): "+target_new)
      print ("CPU Cap: "+target3_new)
    if str(now.hour) not in hours and t1 > target4_new and cpu1 > target3_new:
      wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
      status=False
      print ("Current Temperature: "+t1)
      print ("CPU Temperature: "+cpu1)
      print ("Target (Night): "+target_new)
      print ("CPU Cap: "+target3_new)
    
  else:
    wiringpi.digitalWrite(0, 0) # sets port 0 to OFF
    status=False

  print("Current heat status : "+str(status))
  print("Current relay mode : "+mode)

  # If there has been a change in state save status
  if status!=prevPumpStatus or mode!=prevPumpMode:
    booststart=time.time()
    saveStatus(mode,status,booststart)
  else:
    print("No change in status so don't save")

  return status

def target_new():

  target_x=getTarget2()
  for i in range(0, len(target_x)):
      target_new=(target_x[i])

  return target_new

def target_new1():

  target_x=getTarget()
  for i in range(0, len(target_x)):
      target_new1=(target_x[i])

  return target_new1

def target_new2():

  target_x=getTarget4()
  for i in range(0, len(target_x)):
      target_new2=(target_x[i])

  return target_new2
