'''
Created on 2013.09.07.
'''

from threading import Thread
import time
import logging
import os

from node.sensor.sensor_type import SensorType
from node.sensor.sensor_collector import TempHumCollector
from node.sensor.sensor_collector import LuxCollector
from node.sensor.sensor_collector import DistanceCollector
from node.sensor.sensor_collector import MotionCollector
from node.sensor.sensor_collector import PowerCollector
from node.sensor.device_controller import RelayController
from node.sensor.device_controller import MotorController
from node.communication.log_sender import LogSender
from node.communication.log_message import LogMessage
from config.config import SensorConfig
from config.config import MqttConfig
from config.config import Config

class SensorDaemon(object):
    
    tempThread = None
    luxThread = None
    distanceThread = None
    motionThread = None
    powerThread = None
    motorThread = None
    
    runTemp = False;
    runLux = False;
    runDistance = False;
    runMotion = False;
    runPower = False; 
    runMotor = False;

    def __init__(self):
        '''
        Constructor
        '''
    
    def startTempHumDaemon(self):
        if self.tempThread == None:
            self.tempThread = Thread(target=self.logTempHum, args=(SensorType.TEMP_HUM,))
        self.runTemp = True
        self.tempThread.start()
        
    def stopTempHumDaemon(self):
        self.runTemp = False
        self.tempThread = None
    
    def startLuxDaemon(self):
        if self.luxThread == None:
            self.luxThread = Thread(target=self.logLux)
        self.runLux = True
        self.luxThread.start()
        
    def stopLuxDaemon(self):
        self.runLux = False
        self.luxThread = None
        
    def startDistanceDaemon(self):
        if self.distanceThread == None:
            self.distanceThread = Thread(target=self.logDistance)
        self.runDistance = True
        self.distanceThread.start()

    def stopDistanceDaemon(self):
        self.runDistance = False
        self.distanceThread = None

    def startMotionDaemon(self):
        if self.motionThread == None:
            self.motionThread = Thread(target=self.logMotion)
        self.runMotion = True
        self.motionThread.start()

    def stopMotionDaemon(self):
        self.runMotion = False
        self.motionThread = None

    def startPowerDaemon(self):
        if self.powerThread == None:
            self.powerThread = Thread(target=self.logPower)
        self.runPower = True
        self.powerThread.start()

    def stopPowerDaemon(self):
        self.runPower = False
        self.powerThread = None
        
    def startMotorDaemon(self): 
        if self.motorThread == None: 
            self.motorThread = Thread(target=self.useMotor) 
        self.runMotor = True
        self.motorThread.start() 
          
    def stopMotorDaemon(self): 
        self.runMotor = False
        self.motorThread = None

    def logTempHum(self, sensorType):
        dataCollector = TempHumCollector()
        logSender = LogSender()
        #logSender.connect()
        while(True and self.runTemp == True):
            if sensorType == SensorType.TEMP_HUM:
                dataCollector.readTempHum()
                #sensorMessage = LogMessage(1, int(round(time.time() * 1000)))
                #sensorMessage.data.append(dataCollector.tempData)
                #sensorMessage.data.append(dataCollector.humData)
            else:
                sensorMessage = 0
            #logSender.sendLog(MqttConfig.TOPIC_LOG_TEMP_HUM, sensorMessage)
                #if Config.DEVELOPER_MODE_ON:
                #logging.log(logging.DEBUG, sensorMessage)
                #logging.info(sensorMessage)
            time.sleep(SensorConfig.TIME_BETWEEN_TWO_MEASUREMENT_IN_SEC)
    
    def logLux(self):
        dataCollector = LuxCollector()
        logSender = LogSender()
        #logSender.connect()
        while(True and self.runLux == True):
            dataCollector.readLux()
            sensorMessage = LogMessage(1, int(round(time.time() * 1000)))
            sensorMessage.data.append(dataCollector.luxData)
            #logSender.sendLog(MqttConfig.TOPIC_LOG_LUX, sensorMessage)
            if Config.DEVELOPER_MODE_ON:
                logging.log(logging.DEBUG, sensorMessage)
                logging.info(sensorMessage)
            time.sleep(SensorConfig.TIME_BETWEEN_TWO_MEASUREMENT_IN_SEC)
        
    def logDistance(self):
        dataCollector = DistanceCollector()
        relayController = RelayController(SensorConfig.GPIO_RELAY_IN_1)
        logSender = LogSender()
        #logSender.connect()
        isTriggered = False
        sensorMessage = None
        triggerTime = 0
        while(True and self.runDistance == True):
            dataCollector.readDistance()
            if dataCollector.distanceData != None:
                if SensorConfig.DISTANCE_TRIGGER_STANDBY_START <= dataCollector.distanceData.value <= SensorConfig.DISTANCE_TRIGGER_STANDBY_END:
                    isTriggered = True
                    triggerTime = int(round(time.time() * 1000))
                if isTriggered:
                    if SensorConfig.DISTANCE_TRIGGER_ACTION_START <= dataCollector.distanceData.value <= SensorConfig.DISTANCE_TRIGGER_ACTION_END:
                        actionTime = int(round(time.time() * 1000)) - triggerTime
                        if  actionTime <= 3000:
                            sensorMessage = LogMessage(1, int(round(time.time() * 1000)))
                            sensorMessage.data.append(dataCollector.distanceData)
                            #logSender.sendLog(MqttConfig.TOPIC_LOG_DISTANCE, sensorMessage)
			    relayController.switch()
			    print "A tavolsagmero kapcsolt!"
                            isTriggered = False
                        else:
                            isTriggered = False
            if Config.DEVELOPER_MODE_ON:
                logging.log(logging.DEBUG, sensorMessage)
                logging.info(sensorMessage)
            time.sleep(SensorConfig.TIME_FOR_ACTION_CHECK)

    def logMotion(self):
        dataCollector = MotionCollector()
        relayController = RelayController(SensorConfig.GPIO_RELAY_IN_4)
        logSender = LogSender()
        #logSender.connect()
        startTime = 0
	sensorMessage = None
        while(True and self.runMotion == True):
            dataCollector.readMotion()
            if dataCollector.motionData != None:
                sensorMessage = LogMessage(1, int(round(time.time() * 1000)))
                sensorMessage.data.append(dataCollector.motionData)
                #logSender.sendLog(MqttConfig.TOPIC_LOG_MOTION, sensorMessage)
                if dataCollector.motionData.value == 1:
                    startTime = int(round(time.time() * 1000))
                    relayController.setOn()
            timeGap = int(round(time.time() * 1000)) - startTime
            if timeGap >= 8000:
                relayController.setOff()
            if Config.DEVELOPER_MODE_ON:
                logging.log(logging.DEBUG, sensorMessage)
                logging.info(sensorMessage)
            time.sleep(SensorConfig.TIME_FOR_ACTION_CHECK)

    def logPower(self):
        dataCollector = PowerCollector()
        logSender = LogSender()
        #logSender.connect()
        while(True and self.runPower == True):
            dataCollector.readPowerInWatt()
            if dataCollector.powerData != None:
                sensorMessage = LogMessage(1, int(round(time.time() * 1000)))
                sensorMessage.data.append(dataCollector.powerData)
                #logSender.sendLog(MqttConfig.TOPIC_LOG_POWER, sensorMessage)
		self.stopTempHumDaemon()
		time.sleep(1)
		self.startTempHumDaemon()
            if Config.DEVELOPER_MODE_ON:
                logging.log(logging.DEBUG, sensorMessage)
                logging.info(sensorMessage)
            time.sleep(SensorConfig.TIME_BETWEEN_TWO_MEASUREMENT_IN_SEC-1)
