'''
Created on 2013.09.07.
'''

import sys

from node.sensor.sensor_daemon import SensorDaemon

def main():
    sys.path.append('/home/pi/ahead')
    sensorDaemon = SensorDaemon()
    sensorDaemon.startTempHumDaemon()
    sensorDaemon.startLuxDaemon()
    sensorDaemon.startDistanceDaemon()
    sensorDaemon.startMotionDaemon()
    sensorDaemon.startPowerDaemon()
    print("OS Platform: " + sys.platform)
    print("Main thread finished!")
    return 0

if __name__ == '__main__':
    main()
