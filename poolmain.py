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
import asyncio
import pickle
from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo, Sensor, SensorInfo, Select, SelectInfo
from paho.mqtt.client import Client, MQTTMessage


logFormat='%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat,filename='/home/pi/pool/logs/main.log',level=logging.WARNING)
logging.info('Main start')

# Check current saved status and create pickle files
# if they don't already exist
p.checkStatus()
p.checkSchedule()
p.checkTarget()
p.checkTarget2()
p.checkTarget3()
p.checkTarget4()
p.checkTarget5()
p.checkTarget6()

# Get the IDs of the DS18B20 temp sensors
mySensorIDs=p.getSensorIDs()

# Set number of seconds to wait before updating relay
loopSendData=c.LOOPSENDDATA
async def main():

    program_starts = time.time()
    loopCounter=0

# Configure the required parameters for the MQTT broker
    mqtt_settings = Settings.MQTT(host=c.MQTTHOST, username=c.MQTTUSER, password=c.MQTTPASS)

# Define the device. At least one of `identifiers` or `connections` must be supplied
    device_info = DeviceInfo(name="Shed 1", identifiers="device_id")

# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_day_target = SelectInfo(name="Day Target", unique_id="select_info_day_target", options=["15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_day_target(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Day target changed to: ' + payload )
        target = [payload]
        p.saveTarget(target)

        my_selection_day_target = Select(Settings(mqtt=mqtt_settings, entity=select_info_day_target), my_callback_day_target)
        my_selection_day_target.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
    
# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_night_target = SelectInfo(name="Night Target", unique_id="select_info_night_target", options=["8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_night_target(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Night target changed to: ' + payload )
        target4 = [payload]
        p.saveTarget4(target4)

        my_selection_night_target = Select(Settings(mqtt=mqtt_settings, entity=select_info_night_target), my_callback_night_target)
        my_selection_night_target.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
    
# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_boost_target = SelectInfo(name="Boost Target", unique_id="select_info_boost_target", options=["15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_boost_target(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Boost target changed to: ' + payload )
        target2 = [payload]
        p.saveTarget2(target2)

        my_selection_boost_target = Select(Settings(mqtt=mqtt_settings, entity=select_info_boost_target), my_callback_boost_target)
        my_selection_boost_target.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
    
# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_cpu_cap = SelectInfo(name="Cpu Cap", unique_id="select_info_cpu_cap", options=["58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_cpu_cap(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Cpu Cap changed to: ' + payload )
        target3 = [payload]
        p.saveTarget3(target3)

        my_selection_cpu_cap = Select(Settings(mqtt=mqtt_settings, entity=select_info_cpu_cap), my_callback_cpu_cap)
        my_selection_cpu_cap.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))

# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_on_target = SelectInfo(name="On Target", unique_id="select_info_on_target", options=["93", "94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_on_target(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('On target changed to: ' + payload )
        target5 = [payload]
        p.saveTarget5(target5)

        my_selection_on_target = Select(Settings(mqtt=mqtt_settings, entity=select_info_on_target), my_callback_on_target)
        my_selection_on_target.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
    
# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_off_target = SelectInfo(name="Off Target", unique_id="select_info_of_target", options=["-7", "-6", "-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "5", "6", "7", "8"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_off_target(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Off target changed to: ' + payload )
        target6 = [payload]
        p.saveTarget6(target6)

        my_selection_off_target = Select(Settings(mqtt=mqtt_settings, entity=select_info_off_target), my_callback_off_target)
        my_selection_off_target.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
          
# A selection list can be added to the same device, by re-using the DeviceInfo instance previously defined

    select_info_mode = SelectInfo(name="Mode", unique_id="select_info_mode", options=["on", "boost", "off", "auto"], device=device_info)

# To receive state commands from HA, define a callback function:
    def my_callback_mode(client: Client, user_data, message: MQTTMessage):
      try:
        payload = message.payload.decode()
        print('Mode changed to: ' + payload )
        mode = payload
        p.pumpUpdate(mode)
        
        my_selection_mode = Select(Settings(mqtt=mqtt_settings, entity=select_info_mode), my_callback_mode)
        my_selection_mode.write_config()

      except Exception as ex:

        print(time.asctime( time.localtime(time.time()) ) + " This error occurred: " + str(ex))
          
    while True:

      now = time.time()
      looptime = now-program_starts

      if looptime >= loopSendData:
        looptime=0
        loopCounter+=1
        if loopCounter == loopSendData:
        # Read current schedule, pump status and mode
        # as it may have been changed by web interface since last loop
          myHours=p.getSchedule()
          target=p.getTarget()
          target2=p.getTarget2()
          target3=p.getTarget3()
          target4=p.getTarget4()
          target5=p.getTarget5()
          target6=p.getTarget6()
          myPumpMode,myPumpStatus,booststart=p.getStatus()

          # Deal with pump based on current mode
          myPumpStatus=p.pumpUpdate(myPumpMode)

          temp1,temp2=p.readTemps(mySensorIDs,c.TEMPUNIT)
          cputemp=p.cpu()

          # An additional sensor can be added to the same device, by re-using the DeviceInfo instance previously defined
          panel_sensor_info = SensorInfo(name="Panel Temperature", device_class="temperature", unit_of_measurement="°C", unique_id="panel_temperature", device=device_info)
          panel_settings = Settings(mqtt=mqtt_settings, entity=panel_sensor_info)

          # Instantiate the sensor
          mysensor1 = Sensor(panel_settings)

          # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
          mysensor1.set_state(temp1)

          # An additional sensor can be added to the same device, by re-using the DeviceInfo instance previously defined
          enclosure_sensor_info = SensorInfo(name="Enclosure Temperature", device_class="temperature", unit_of_measurement="°C", unique_id="enclosure_temperature", device=device_info)
          enclosure_settings = Settings(mqtt=mqtt_settings, entity=enclosure_sensor_info)

          # Instantiate the sensor
          mysensor2 = Sensor(enclosure_settings)

          # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
          mysensor2.set_state(temp2)

          # An additional sensor can be added to the same device, by re-using the DeviceInfo instance previously defined
          cpu_sensor_info = SensorInfo(name="Cpu Temperature", device_class="temperature", unit_of_measurement="°C", unique_id="cpu_temperature", device=device_info)
          cpu_settings = Settings(mqtt=mqtt_settings, entity=cpu_sensor_info)

          # Instantiate the sensor
          mysensor3 = Sensor(cpu_settings)

          # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
          mysensor3.set_state(cputemp)

          # An additional sensor can be added to the same device, by re-using the DeviceInfo instance previously defined
          relay_sensor_info = BinarySensorInfo(name="Relay status", device_class="motion", unique_id="relay_status", device=device_info)
          relay_settings = Settings(mqtt=mqtt_settings, entity=relay_sensor_info)

          # Instantiate the sensor
          mysensor4 = BinarySensor(relay_settings)

          # Change the state of the sensor, publishing an MQTT message that gets picked up by HA

          if myPumpStatus == True:

             mysensor4.on()

          else:

             mysensor4.off()
            
          print('=================================================================================' )
          loopCounter=0
          program_starts = time.time()

    await asyncio.sleep(1)

if __name__ == '__main__':
  asyncio.run(main())
