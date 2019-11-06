#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#     Pool Monitor System
#          poolweb.py
#
# This is the web front-end script.
#
# It serves a status page and allows users to set the
# pump mode and edit the schedule. If Alexa lines are
# uncommented then the system can respond to a suitable
# Skill.
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
import datetime
import logging
import hashlib
import config as c
import poollib as p
from flask import Flask,flash,jsonify,redirect,request,render_template,url_for,session,escape

# Alexa Upgrade - uncomment line below 1/5
#from flask_ask import Ask, statement

app = Flask(__name__)
app.secret_key = c.FLASKSECRET

# Alexa Upgrade - uncomment line below 2/5
#ask = Ask(app, '/')

logFormat='%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat,filename='/home/pi/pool/logs/web.log',level=logging.DEBUG)
logging.info('Web start')

mySensorIDs=[]
myPumpMode=''
myPumpStatus=False

@app.route('/')
def index():
    global mySensorIDs
    if 'username' in session:
      temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
      myPumpMode,myPumpStatus,timestamp=p.getStatus()
      timeStamp='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
      data={'t1': temp1,
            't2': temp2,
            'tu': c.TEMPUNIT,
            'pm': myPumpMode,
            'ps': myPumpStatus,
            'ts': timeStamp,
            'user': escape(session['username'])
            }
      return render_template('index.html',data=data)
    else:
      return redirect(url_for('login'))

@app.route('/on/')
def on():
    global mySensorIDs,myPumpStatus,myPumpMode
    myPumpMode='on'
    myPumpStatus=p.pumpUpdate(myPumpMode)
    return redirect(url_for('index'))

@app.route('/off/')
def off():
    global mySensorIDs,myPumpStatus,myPumpMode
    myPumpMode='off'
    myPumpStatus=p.pumpUpdate(myPumpMode)
    return redirect(url_for('index'))

@app.route('/auto/')
def auto():
    global mySensorIDs,myPumpStatus,myPumpMode
    myPumpMode='auto'
    myPumpStatus=p.pumpUpdate(myPumpMode)
    return redirect(url_for('index'))

@app.route('/boost/')
def boost():
    global mySensorIDs,myPumpStatus,myPumpMode
    myPumpMode='boost'
    myPumpStatus=p.pumpUpdate(myPumpMode)
    return redirect(url_for('index'))

@app.route('/debug/')
def debug():
    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
    sensorIDs=p.getSensorIDs()
    mode,status,booststart=p.getStatus()
    hours = p.getSchedule()
    timeStamp='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    
    if mode=="boost":
      boostremain=3600+booststart-time.time()
    else:
      boostremain=0  
    
    data={'id1': sensorIDs[0],
          'id2': sensorIDs[1],
          't1' : temp1,
          't2' : temp2,
          'tu' : c.TEMPUNIT,
          'pm' : mode,
          'ps' : status,
          'hrs': hours,
          'ts' : timeStamp,
          'bt' : booststart,
          'br' : boostremain
         }
    return render_template('debug.html',data=data)

@app.route('/schedule/', methods=['GET','POST'])
def schedule():
    if request.method == 'POST':
        myHours = request.form.getlist("hours")
        p.saveSchedule(myHours)
        flash('Schedule saved','info')
    else:
      myHours=p.getSchedule()
    return render_template('schedule.html',hours=myHours)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from submitted form
        userName=escape(request.form['username'])
        passWord=escape(request.form['password'])
        # Convert password to hash and compare to stored hash
        passWordHash=hashlib.sha256(passWord.encode('utf-8')).hexdigest()
        if userName==c.USERNAME and passWordHash==c.USERHASH:
          session['username']='admin'
          return redirect(url_for('index'))
        else:
          time.sleep(2)
          session.pop('username', None)
          flash('Sorry. Better luck next time.','danger')
    else:
      flash('Please enter your details.','info')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove username from the session
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/status')
def status():
    # Return temps and pump mode in Json format to any
    # system that calls the /status URL. e.g. Home Assistant
    global mySensorIDs,myPumpStatus,myPumpMode
    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
    
    if myPumpStatus==True:
        myPumpStatus="On"
    else:
        myPumpStatus="Off"
    
    return jsonify(watertemp=temp1,airtemp=temp2,pumpmode=myPumpMode,pumpstatus=myPumpStatus)

# Alexa Upgrade - uncomment line below 3/5
#@ask.intent('StatusIntent')
def alexa_StatusIntent():
    global mySensorIDs,myPumpStatus,myPumpMode
    title='Pool Monitor Status'
    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)

    text='The water temperature is '+temp1+' degrees.'
    text=text+' The air temperature is '+temp2+' degrees.'
    text=text+' Pump mode is '+myPumpMode
    if myPumpStatus==True:
        text=text+' and the pump is ON.'
    else:
        text=text+' and the pump is OFF.'

    return statement(text).simple_card(title,text)

# Alexa Upgrade - uncomment line below 4/5
#@ask.intent('PumpControlIntent')
def alexa_PumpControlIntent(command):
    global mySensorIDs,myPumpStatus,myPumpMode
    title='Pool Monitor Pump Control'
    if command=='on' or command=='off':
        text='Turning pump '+command
        myPumpMode=command
        myPumpStatus=p.pumpUpdate(myPumpMode)
    else:
        text='You can only turn the pump ON or OFF'

    return statement(text).simple_card(title,text)

if __name__ == '__main__':
    mySensorIDs=p.getSensorIDs()
    myPumpMode,myPumpStatus,timestamp=p.getStatus()

    # Default Flask port
    flaskPort=5000

    # Alexa Upgrade - uncomment line below 5/5
    #flaskPort=80

    app.run(host='0.0.0.0', port=flaskPort, debug=False)
