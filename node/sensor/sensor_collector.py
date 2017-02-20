'''
Created on 2013.09.07.
'''
import subprocess
import os
import re
import sys
import time, datetime

import RPi.GPIO as GPIO
import smbus
from libs.Adapy.Adafruit_I2C.Adafruit_I2C import Adafruit_I2C

from node.communication.log_message import LogMessage
from node.sensor.sensor_data import SensorData
from node.sensor.sensor_type import SensorType
from config.config import SensorConfig
from config.config import Config

class TempHumCollector(object):
    
    tempData = None
    humData = None

    def __init__(self):
	GPIO.setmode(GPIO.BCM)
        GPIO.setup(SensorConfig.GPIO_TEMP_HUM, GPIO.IN)
        #print("Temperature and humidity sensor data collector created.")
        self.tempData = SensorData(SensorType.TEMPERATURE, 4)
        self.humData = SensorData(SensorType.HUMIDITY, 4)
        
    def readTempHum(self):
        output = ""
        try:
            os.chdir('/home/pi/ahead/libs/Adapy/Adafruit_DHT_Driver')
            output = subprocess.check_output(["sudo", "./Adafruit_DHT", str(SensorConfig.SENSOR_MODEL_TEMP), str(SensorConfig.GPIO_TEMP_HUM)])
        except OSError:
            print("No such path.")
        except:
            print("Unknown error.")
        finally:
            if(output != ""):
                self.setTempData(output)
                self.setHumData(output)
            
    def setTempData(self, sensorOutput):
        matches = re.search("Temp =\s+([0-9.]+)", sensorOutput)
        if(matches):
            self.tempData = SensorData(SensorType.TEMPERATURE, float(matches.group(1)))
	    print "A jelenlegi homerseklet: " + str(float(matches.group(1))) + " C"

    def setHumData(self, sensorOutput):
        matches = re.search("Hum =\s+([0-9.]+)", sensorOutput)
        if(matches):
            self.humData = SensorData(SensorType.HUMIDITY, float(matches.group(1)))
	    print "A jelenlegi paratartalom: " + str(float(matches.group(1))) + " %"

class LuxCollector(object):
    # ## by huelke
    # ## http://www.adafruit.com/forums/viewtopic.php?f=8&t=34922&sid=dada906dd036fd7b07b6874748dae2d4&start=75
  
    i2c = None
    luxData = None

    def __init__(self, address=0x39, pause=0.8):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.pause = pause
        self.gain = 0  # no gain preselected
        self.i2c.write8(0x80, 0x03)  # enable the device
        self.luxData = SensorData(SensorType.LUX, 0)

    def setGain(self, gain=1):
        """ Set the gain """
        if (gain != self.gain):
            if (gain == 1):
                self.i2c.write8(0x81, 0x02)  # set gain = 1X and timing = 402 mSec
                if(Config.DEVELOPER_MODE_ON):
                    print "Setting low gain"
            else:
                self.i2c.write8(0x81, 0x12)  # set gain = 16X and timing = 402 mSec
                if(Config.DEVELOPER_MODE_ON):
                    print "Setting high gain"
            self.gain = gain;  # safe gain for calculation
            time.sleep(self.pause)  # pause for integration (self.pause must be bigger than integration time)

    def readWord(self, reg):
        """Reads a word from the I2C device"""
        try:
            wordval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(wordval)
            #if(Config.DEVELOPER_MODE_ON):
                #print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, wordval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readFull(self, reg=0x8C):
        """Reads visible+IR diode from the I2C device"""
        return self.readWord(reg);

    def readIR(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        return self.readWord(reg);

    def readLux(self, gain=1):
        """Grabs a lux reading either with autoranging (gain=0) or with a specified gain (1, 16)"""
        if (gain == 1 or gain == 16):
            self.setGain(gain)  # low/highGain
            ambient = self.readFull()
            IR = self.readIR()
        elif (gain == 0):  # auto gain
            self.setGain(16)  # first try highGain
            ambient = self.readFull()
            if (ambient < 65535):
                IR = self.readIR()
            if (ambient >= 65535 or IR >= 65535):  # value(s) exeed(s) datarange
                self.setGain(1)  # set lowGain
                ambient = self.readFull()
                IR = self.readIR()
        if (self.gain == 1):
            ambient *= 16  # scale 1x to 16x
            IR *= 16  # scale 1x to 16x
        ratio = (IR / float(ambient))  # changed to make it run under python 2
        #if(Config.DEVELOPER_MODE_ON):
            #print "IR Result", IR
            #print "Ambient Result", ambient
        if ((ratio >= 0) & (ratio <= 0.52)):
            lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio ** 1.4))
        elif (ratio <= 0.65):
            lux = (0.0229 * ambient) - (0.0291 * IR)
        elif (ratio <= 0.80):
            lux = (0.0157 * ambient) - (0.018 * IR)
        elif (ratio <= 1.3):
            lux = (0.00338 * ambient) - (0.0026 * IR)
        elif (ratio > 1.3):
            lux = 0
        self.luxData = SensorData(SensorType.LUX, lux)
	print "A jelenlegi fenyerosseg: " +str(lux) + " Lux"

class DistanceCollector(object):

    distanceData = None
    arrgpio = None
    
    def __init__(self, decpulsetrigger=0.0001, inttimeout=2100):
        self.decpulsetrigger = decpulsetrigger  # Trigger duration
        self.inttimeout = inttimeout  # Number of loop iterations before timeout called
        # Which GPIO's are used [0]=BCM Port Number [1]=BCM Name [2]=Use [3]=Pin
        self.arrgpio = [(SensorConfig.GPIO_DISTANCE_ECHO, "GPIO0", "Echo", 11), (SensorConfig.GPIO_DISTANCE_TRIG, "GPIO7", "Trig", 7)]
        # Set GPIO Channels
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.arrgpio[0][0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.arrgpio[1][0], GPIO.OUT)
        GPIO.output(self.arrgpio[1][0], False)
        if(Config.DEVELOPER_MODE_ON):
            GPIO.setwarnings(True)
            print("Distance sensor meter created")
        else:
            GPIO.setwarnings(False)

    def readDistance(self):
        # Trigger high for 0.0001s then low
        GPIO.output(self.arrgpio[1][0], True)
        time.sleep(self.decpulsetrigger)
        GPIO.output(self.arrgpio[1][0], False)
        # Wait for echo to go high (or timeout)
        intcountdown = self.inttimeout
        while (GPIO.input(self.arrgpio[0][0]) == 0 and intcountdown > 0):
            intcountdown = intcountdown - 1
        # If echo is high
        if intcountdown > 0:
            # Start timer and init timeout countdown
            echostart = time.time()
            intcountdown = self.inttimeout
            # Wait for echo to go low (or timeout)
            while (GPIO.input(self.arrgpio[0][0]) == 1 and intcountdown > 0):
                intcountdown = intcountdown - 1
            # Stop timer
            echoend = time.time()
            # Echo duration
            echoduration = echoend - echostart
        # Display distance
        if intcountdown > 0:
            intdistance = (echoduration * 1000000) / 58
            #if(Config.DEVELOPER_MODE_ON):
                #print "Distance = " + str(intdistance) + "cm"
            self.distanceData = SensorData(SensorType.DISTANCE, intdistance)
        else:
            self.distanceData = None
            if(Config.DEVELOPER_MODE_ON):
                print "Distance - timeout"

class MotionCollector(object):
    
    motionData = None
    
    def __init__(self):
        # Use BCM GPIO references, instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SensorConfig.GPIO_MOTION, GPIO.IN)
        self.currentState = 0
        self.previousState = 0
        if Config.DEVELOPER_MODE_ON:
            print "Motion sensor meter created"
        
    def readMotion(self):
        self.currentState = GPIO.input(SensorConfig.GPIO_MOTION)
        if self.currentState == 1 and self.previousState == 0:
            if Config.DEVELOPER_MODE_ON:
                print "A mozgaserzekelo: mozgast eszlelt "
            self.motionData = SensorData(SensorType.MOTION, 1)
            self.previousState = 1
        elif self.currentState == 0 and self.previousState == 1:
            # PIR has returned to ready state
            if Config.DEVELOPER_MODE_ON:
                print "A mozgaserzekelo: nyugalmi allapot "
            self.motionData = SensorData(SensorType.MOTION, 0)
            self.previousState = 0
        else:
            self.motionData = None

class PowerCollector(object):

# ===========================================================================
# INA219 Class
# ===========================================================================

    i2c = None

# ===========================================================================
#   I2C ADDRESS/BITS
# ==========================================================================
    __INA219_ADDRESS = 0x40  # 1000000 (A0+A1=GND)
    __INA219_READ = 0x01
# ===========================================================================

# ===========================================================================
#    CONFIG REGISTER (R/W)
# ===========================================================================
    __INA219_REG_CONFIG = 0x00
# ===========================================================================
    __INA219_CONFIG_RESET = 0x8000  # Reset Bit
    __INA219_CONFIG_BVOLTAGERANGE_MASK = 0x2000  # Bus Voltage Range Mask
    __INA219_CONFIG_BVOLTAGERANGE_16V = 0x0000  # 0-16V Range
    __INA219_CONFIG_BVOLTAGERANGE_32V = 0x2000  # 0-32V Range

    __INA219_CONFIG_GAIN_MASK = 0x1800  # Gain Mask
    __INA219_CONFIG_GAIN_1_40MV = 0x0000  # Gain 1, 40mV Range
    __INA219_CONFIG_GAIN_2_80MV = 0x0800  # Gain 2, 80mV Range
    __INA219_CONFIG_GAIN_4_160MV = 0x1000  # Gain 4, 160mV Range
    __INA219_CONFIG_GAIN_8_320MV = 0x1800  # Gain 8, 320mV Range

    __INA219_CONFIG_BADCRES_MASK = 0x0780  # Bus ADC Resolution Mask
    __INA219_CONFIG_BADCRES_9BIT = 0x0080  # 9-bit bus res = 0..511
    __INA219_CONFIG_BADCRES_10BIT = 0x0100  # 10-bit bus res = 0..1023
    __INA219_CONFIG_BADCRES_11BIT = 0x0200  # 11-bit bus res = 0..2047
    __INA219_CONFIG_BADCRES_12BIT = 0x0400  # 12-bit bus res = 0..4097

    __INA219_CONFIG_SADCRES_MASK = 0x0078  # Shunt ADC Resolution and Averaging Mask
    __INA219_CONFIG_SADCRES_9BIT_1S_84US = 0x0000  # 1 x 9-bit shunt sample
    __INA219_CONFIG_SADCRES_10BIT_1S_148US = 0x0008  # 1 x 10-bit shunt sample
    __INA219_CONFIG_SADCRES_11BIT_1S_276US = 0x0010  # 1 x 11-bit shunt sample
    __INA219_CONFIG_SADCRES_12BIT_1S_532US = 0x0018  # 1 x 12-bit shunt sample
    __INA219_CONFIG_SADCRES_12BIT_2S_1060US = 0x0048  # 2 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_4S_2130US = 0x0050  # 4 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_8S_4260US = 0x0058  # 8 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_16S_8510US = 0x0060  # 16 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_32S_17MS = 0x0068  # 32 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_64S_34MS = 0x0070  # 64 x 12-bit shunt samples averaged together
    __INA219_CONFIG_SADCRES_12BIT_128S_69MS = 0x0078  # 128 x 12-bit shunt samples averaged together

    __INA219_CONFIG_MODE_MASK = 0x0007  # Operating Mode Mask
    __INA219_CONFIG_MODE_POWERDOWN = 0x0000
    __INA219_CONFIG_MODE_SVOLT_TRIGGERED = 0x0001
    __INA219_CONFIG_MODE_BVOLT_TRIGGERED = 0x0002
    __INA219_CONFIG_MODE_SANDBVOLT_TRIGGERED = 0x0003
    __INA219_CONFIG_MODE_ADCOFF = 0x0004
    __INA219_CONFIG_MODE_SVOLT_CONTINUOUS = 0x0005
    __INA219_CONFIG_MODE_BVOLT_CONTINUOUS = 0x0006
    __INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007
# ===========================================================================

# ===========================================================================
#   SHUNT VOLTAGE REGISTER (R)
# ===========================================================================
    __INA219_REG_SHUNTVOLTAGE = 0x01
# ===========================================================================

# ===========================================================================
#   BUS VOLTAGE REGISTER (R)
# ===========================================================================
    __INA219_REG_BUSVOLTAGE = 0x02
# ===========================================================================

# ===========================================================================
#   POWER REGISTER (R)
# ===========================================================================
    __INA219_REG_POWER = 0x03
# ===========================================================================

# ==========================================================================
#    CURRENT REGISTER (R)
# ===========================================================================
    __INA219_REG_CURRENT = 0x04
# ===========================================================================

# ===========================================================================
#    CALIBRATION REGISTER (R/W)
# ===========================================================================
    __INA219_REG_CALIBRATION = 0x05
# ===========================================================================

    powerData = None
    currentData = None

    # Constructor
    def __init__(self, address=0x40, debug=False):
        self.i2c = Adafruit_I2C(address, debug=False)
        self.address = address
        self.ina219SetCalibration_32V_2A()
        if Config.DEVELOPER_MODE_ON:
            print("Power sensor meter created")
        
    def ina219SetCalibration_32V_2A(self):
        self.ina219_currentDivider_mA = 10  # Current LSB = 100uA per bit (1000/100 = 10)
        self.ina219_powerDivider_mW = 2  # Power LSB = 1mW per bit (2/1)
        
        # Set Calibration register to 'Cal' calculated above    
        bytes = [(0x1000 >> 8) & 0xFF, 0x1000 & 0xFF]
        self.i2c.writeList(self.__INA219_REG_CALIBRATION, bytes)
        
        # Set Config register to take into account the settings above
        config = self.__INA219_CONFIG_BVOLTAGERANGE_32V | \
                 self.__INA219_CONFIG_GAIN_8_320MV | \
                 self.__INA219_CONFIG_BADCRES_12BIT | \
                 self.__INA219_CONFIG_SADCRES_12BIT_1S_532US | \
                 self.__INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS
        
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.i2c.writeList(self.__INA219_REG_CONFIG, bytes)
        
    def getBusVoltage_raw(self):
        result = self.i2c.readU16(self.__INA219_REG_BUSVOLTAGE)
        
        # Shift to the right 3 to drop CNVR and OVF and multiply by LSB
        return (result >> 3) * 4
        
    def getShuntVoltage_raw(self):
        result = self.i2c.readList(self.__INA219_REG_SHUNTVOLTAGE, 2)
        if (result[0] >> 7 == 1):
            value = ((result[0] & 0xF0) | (result[1])) - 1
            return ~value
        else:
            return (result[0] << 8) | (result[1])
        
    def getCurrent_raw(self):
        result = self.i2c.readList(self.__INA219_REG_CURRENT, 2)
        if (result[0] >> 7 == 1):
            value = ((result[0] & 0xF0) | (result[1])) - 1
            return ~value
        else:
            return (result[0] << 8) | (result[1])

    def getPower_raw(self):
        result = self.i2c.readList(self.__INA219_REG_POWER, 2)
        if (result[0] >> 7 == 1):
            value = ((result[0] & 0xF0) | (result[1])) - 1
            return ~value
        else:
            return (result[0] << 8) | (result[1])

    def getShuntVoltage_mV(self):
        value = self.getShuntVoltage_raw()
        return value * 0.01
        
    def getBusVoltage_V(self):
        value = self.getBusVoltage_raw()
        return value * 0.001
        
    def getCurrent_mA(self):
        valueDec = self.getCurrent_raw()
        valueDec /= self.ina219_currentDivider_mA
        return valueDec
    
    def getPower_mW(self):
        valueDec = self.getPower_raw()
        valueDec /= self.ina219_powerDivider_mW
        return valueDec
    
    def readPowerInWatt(self):
        watt = float(self.getPower_mW()) / 1000
        self.powerData = SensorData(SensorType.POWER, watt)
	print "A LED aramfogyasztasa: " + str(watt) + " Watt"
    
    def readCurrentInAmper(self):
        amper = float(self.getCurrent_mA()) / 1000
        self.currentData = SensorData(SensorType.CURRENT, amper)
    
