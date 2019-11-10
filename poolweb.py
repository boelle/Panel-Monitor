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

app = Flask(__name__)
app.secret_key = c.FLASKSECRET

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
      uptime1=uptime()
      uptime_new=round(uptime1, 2)
      temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
      cpu1=p.cpu()
      myPumpMode,myPumpStatus,timestamp=p.getStatus()
      target = p.getTarget()
      for i in range(0, len(target)):
          target_new=(target[i])
      target2 = p.getTarget2()
      for i in range(0, len(target2)):
          target2_new=(target2[i])
      target3 = p.getTarget3()
      for i in range(0, len(target3)):
          target3_new=(target3[i])
      target4 = p.getTarget4()
      for i in range(0, len(target4)):
          target4_new=(target4[i])
        
      timeStamp='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
      data={'t1': temp1,
            't2': temp2,
            'cu': cpu1,
            'tu': c.TEMPUNIT,
            'pm': myPumpMode,
            'ps': myPumpStatus,
            'ts': timeStamp,
            'tar': target_new,
            'ta2': target2_new,
            'ta3': target3_new,
            'ta4': target4_new,
            'up': uptime_new,
            'user': escape(session['username'])
            }
      return render_template('index.html',data=data)
    else:
      return redirect(url_for('user'))

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
    uptime1=uptime()
    uptime_new=round(uptime1, 2)
    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
    cpu1=p.cpu()
    sensorIDs=p.getSensorIDs()
    mode,status,booststart=p.getStatus()
    hours = p.getSchedule()
    target = p.getTarget()
    target2 = p.getTarget2()
    target3 = p.getTarget3()
    target4 = p.getTarget4()
    timeStamp='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    
    if mode=="boost":
      boostremain=900+booststart-time.time()
    else:
      boostremain=0  
    
    data={'id1': sensorIDs[0],
          'id2': sensorIDs[1],
          't1' : temp1,
          't2' : temp2,
          'cu' : cpu1,
          'tu' : c.TEMPUNIT,
          'pm' : mode,
          'ps' : status,
          'hrs': hours,
          'tar': target,
          'ta2': target2,
          'ta3': target3,
          'ta4': target4,
          'up': uptime_new,
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
        flash('Schedule Saved','info')
    else:
      myHours=p.getSchedule()
    return render_template('schedule.html',hours=myHours)

@app.route('/target/', methods=['GET','POST'])
def target():
    if request.method == 'POST':
        target = request.form.getlist("target")
        p.saveTarget(target)
        flash('Day Temeprature Saved','info')
    else:
      target=p.getTarget()
    return render_template('target.html',target=target)

@app.route('/target2/', methods=['GET','POST'])
def target2():
    if request.method == 'POST':
        target2 = request.form.getlist("target2")
        p.saveTarget2(target2)
        flash('Boost Temperature Saved','info')
    else:
      target2=p.getTarget2()
    return render_template('target2.html',target2=target2)

@app.route('/target3/', methods=['GET','POST'])
def target3():
    if request.method == 'POST':
        target3 = request.form.getlist("target3")
        p.saveTarget3(target3)
        flash('CPU Cap Temperature Saved','info')
    else:
      target3=p.getTarget3()
    return render_template('target3.html',target3=target3)

@app.route('/target4/', methods=['GET','POST'])
def target4():
    if request.method == 'POST':
        target4 = request.form.getlist("target4")
        p.saveTarget4(target4)
        flash('Night Temperature Saved','info')
    else:
      target4=p.getTarget4()
    return render_template('target4.html',target4=target4)

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

@app.route('/user')
def user():
    global mySensorIDs
    temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
    myPumpMode,myPumpStatus,timestamp=p.getStatus()
    target = p.getTarget()
    for i in range(0, len(target)):
        target_new=(target[i])
    target2 = p.getTarget2()
    for i in range(0, len(target2)):
        target2_new=(target2[i])
    target4 = p.getTarget4()
    for i in range(0, len(target4)):
        target4_new=(target4[i])        


    timeStamp='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    data={'t1': temp1,
          't2': temp2,
          'tu': c.TEMPUNIT,
          'pm': myPumpMode,
          'ps': myPumpStatus,
          'tar': target_new,
          'ta2': target2_new,
          'ta4': target4_new,
          'ts': timeStamp
          }
    return render_template('user.html',data=data)

@app.route('/logout')
def logout():
    # Remove username from the session
    session.pop('username', None)
    return redirect(url_for('index'))

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

if __name__ == '__main__':
    mySensorIDs=p.getSensorIDs()
    myPumpMode,myPumpStatus,timestamp=p.getStatus()

    # Default Flask port
    flaskPort=9900

    # Alexa Upgrade - uncomment line below 5/5
    #flaskPort=80

    app.run(host='0.0.0.0', port=flaskPort, debug=False)
