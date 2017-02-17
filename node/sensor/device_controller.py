'''
Created on 2013.09.21.

'''

import RPi.GPIO as GPIO
import time
import os
from threading import Thread
from config.config import SensorConfig

class RelayController(object):
    
    relayGpio = None
    talkThread = None
    motoFwThread = None
    motoBwThread = None

    runMoto = False

    w1 = None
    w2 = None
    w3 = None
    w4 = None

    def __init__(self, relayGpio=SensorConfig.GPIO_RELAY_IN_1, delay=SensorConfig.TIME_MOTOR_SPEED_FAST):
        self.relayGpio = relayGpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relayGpio, GPIO.OUT)
        GPIO.output(self.relayGpio, 1)
        GPIO.setmode(GPIO.BCM) 
        #GPIO.setup(SensorConfig.GPIO_MOTOR_ENABLE, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_1, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_2, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_3, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_4, GPIO.OUT) 
        #GPIO.output(GPIO_MOTOR_ENABLE, 1) 
        self.delay = delay

    def setStep(self, w1, w2, w3, w4): 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_1, w1) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_2, w2) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_3, w3) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_4, w4) 

    def startMotoFw(self):
	while(self.runMoto == True):
            self.setStep(1,0,0,1)
            time.sleep(self.delay)
            self.setStep(1,1,0,0)
            time.sleep(self.delay)
            self.setStep(0,1,1,0)
            time.sleep(self.delay)
            self.setStep(0,0,1,1)
            time.sleep(self.delay)
    
    def setOn(self):
	if(GPIO.input(self.relayGpio) == 1):
		self.talkThread = Thread(target=self.talkOn)
        	self.talkThread.start()
        GPIO.output(self.relayGpio, 0)
	
    def setOff(self):
        GPIO.output(self.relayGpio, 1)
        
    def switch(self):
        GPIO.output(self.relayGpio, not GPIO.input(self.relayGpio))
        if self.motoFwThread == None:
	    self.runMoto = True
            self.motoFwThread = Thread(target=self.startMotoFw)
            self.motoFwThread.start()
	else:
	    self.motoFwThread = None
	    self.runMoto = False
        
    def isRelayOn(self):
        GPIO.input(self.relayGpio)

    def talkOn(self):
	os.system('espeak -vf3 "turning on the light"')
        self.talkThread = None

class MotorController(object):
    
    w1 = None
    w2 = None
    w3 = None
    w4 = None

    def __init__(self, delay=SensorConfig.TIME_MOTOR_SPEED_FAST): 
        GPIO.setmode(GPIO.BCM) 
        #GPIO.setup(GPIO_MOTOR_ENABLE, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_1, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_2, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_3, GPIO.OUT) 
        GPIO.setup(SensorConfig.GPIO_MOTOR_IN_4, GPIO.OUT) 
        #GPIO.output(GPIO_MOTOR_ENABLE, 1) 
        self.delay = delay 
          
    def setStep(w1, w2, w3, w4): 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_1, w1) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_2, w2) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_3, w3) 
        GPIO.output(SensorConfig.GPIO_MOTOR_IN_4, w4) 
          
    def backward1p(steps): 
        for i in range(0, steps): 
            self.setStep(0, 0, 0, 1) 
            time.sleep(self.delay) 
            self.setStep(0, 0, 1, 0) 
            time.sleep(self.delay) 
            self.setStep(0, 1, 0, 0) 
            time.sleep(self.delay) 
            self.setStep(1, 0, 0, 0) 
            time.sleep(self.delay) 
              
    def forward1p(steps):   
        for i in range(0, steps): 
            self.setStep(1, 0, 0, 0) 
            time.sleep(self.delay) 
            self.setStep(0, 1, 0, 0) 
            time.sleep(self.delay) 
            self.setStep(0, 0, 1, 0) 
            time.sleep(self.delay) 
            self.setStep(0, 0, 0, 1) 
            time.sleep(self.delay) 
              
    def backward2p(steps):   
        for i in range(0, steps): 
            setStep(0, 0, 1, 1) 
            time.sleep(self.delay) 
            setStep(0, 1, 1, 0) 
            time.sleep(self.delay) 
            setStep(1, 1, 0, 0) 
            time.sleep(self.delay) 
            setStep(1, 0, 0, 1) 
            time.sleep(self.delay) 
  
    def forward2p(steps):   
        for i in range(0, steps): 
            setStep(1, 0, 0, 1) 
            time.sleep(self.delay) 
            setStep(1, 1, 0, 0) 
            time.sleep(self.delay) 
            setStep(0, 1, 1, 0) 
            time.sleep(self.delay) 
            setStep(0, 0, 1, 1) 
            time.sleep(self.delay) 
