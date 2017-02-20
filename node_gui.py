'''
Created on 2013.09.22.
'''

import sys
import time
import threading
from threading import Thread
import Tkinter
import ttk
import tkMessageBox

from node.sensor.sensor_daemon import SensorDaemon
from config.config import SensorConfig
from node.sensor.sensor_type import SensorType

class NodeUI(object):
    
    sensorDaemon = None
    
    tempGpio = None
    tempLabel = None

    def __init__(self):
        print("Node gui created")
        
    def startTemperatureDaemon(self):
        self.sensorDaemon.startTempHumDaemon()
        self.tempLabel.config(text="RUNNING")        
        self.tempLabel.config(foreground=ViewValues.greenHex)

    def stopTemperatureDaemon(self):
        self.sensorDaemon.stopTempHumDaemon()
        self.tempLabel.config(text="STOPPED")        
        self.tempLabel.config(foreground=ViewValues.redHex)
        
    def setTempGpio(self):
        SensorConfig.GPIO_TEMP_HUM = self.tempGpio.get()
        print SensorConfig.GPIO_TEMP_HUM 

    def createWindow(self):
        
        self.sensorDaemon = SensorDaemon()
        
        # main window
        rootLayout = Tkinter.Tk()
        rootLayout.title("AHEaD Stone - Node")
        rootLayout.minsize(320, 160)
        
        # grid frame background
        frame = ttk.Frame(rootLayout, padding="8 8 8 8")
        frame.grid(column=0, row=0, sticky=(Tkinter.N, Tkinter.W, Tkinter.E, Tkinter.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # label and entry for temperature, daemon start/stop
        tempLabel = ttk.Label(frame, text="Homerseklet: (C)", font=ViewValues.boldFont)
        tempLabel.grid(column=1, row=1, sticky=(Tkinter.W, Tkinter.E))
        self.tempGpio = Tkinter.StringVar()
        self.tempGpio.set(8)
	self.tempLabel = ttk.Label(frame, text=self.sensorDaemon.getTempHum(SensorType.TEMP_HUM))
        self.tempLabel.grid(column=2, row=1, sticky=(Tkinter.W, Tkinter.E))
        startTemp = ttk.Button(frame, text="START", command=self.startTemperatureDaemon)
        startTemp.grid(column=1, row=2, sticky=Tkinter.W)
        stopTemp = ttk.Button(frame, text="STOP", command=self.stopTemperatureDaemon)
        stopTemp.grid(column=2, row=2, sticky=Tkinter.W)
        self.tempLabel = ttk.Label(frame, text="STOPPED", foreground=ViewValues.redHex)
        self.tempLabel.grid(column=3, row=2, sticky=(Tkinter.W, Tkinter.E))
        
        # label and entry for motion, daemon start/stop
        motionLabel = ttk.Label(frame, text="Motion GPIO:", font=ViewValues.boldFont)
        motionLabel.grid(column=1, row=3, sticky=(Tkinter.W, Tkinter.E))
        motionGpio = Tkinter.StringVar()
        motionGpio.set(SensorConfig.GPIO_MOTION)
        motionEntry = ttk.Entry(frame, width=8, textvariable=motionGpio)
        motionEntry.grid(column=2, row=3, sticky=(Tkinter.W, Tkinter.E))
        setMotion = ttk.Button(frame, text="Set", command=self.setTempGpio)
        setMotion.grid(column=3, row=3, sticky=Tkinter.W)
        startMotion = ttk.Button(frame, text="START")
        startMotion.grid(column=1, row=4, sticky=Tkinter.W)
        stopMotion = ttk.Button(frame, text="STOP")
        stopMotion.grid(column=2, row=4, sticky=Tkinter.W)
        tempLabel = ttk.Label(frame, text="STOPPED", foreground=ViewValues.redHex)
        tempLabel.grid(column=3, row=4, sticky=(Tkinter.W, Tkinter.E))
        
        for child in frame.winfo_children(): child.grid_configure(padx=5, pady=5)
        
        rootLayout.mainloop()

class ViewValues:
    greenHex = "#2A9E24"
    redHex = "#C41010"
    boldFont = "Helvetica 10 bold"

ui = NodeUI()
ui.createWindow()
