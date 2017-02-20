'''
Created on 2013.09.07.
'''

import json
from mosquitto import Mosquitto
import random

from config.config import MqttConfig

class LogSender(object):

    def __init__(self):
        '''
        Constructor
        '''
        self.client = Mosquitto(str(random.randint(100000, 999999)))
    
    def connect(self):
        self.client.connect(MqttConfig.MQTT_SERVER_URL)
    
    def sendLog(self, topic, logMessage):
        try:
            logJson = json.dumps(logMessage, default=lambda o: o.__dict__, indent=2)
            retVal = self.client.publish(topic, logJson, 1)
            if retVal[0] != 0:
                self.connect()
        except ValueError:
            pass
