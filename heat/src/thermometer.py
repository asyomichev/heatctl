import threading 
import random
import logging
import time
import serial
from event import Event

class RawReadingEvent(Event):
    def __init__(self, sensor, temperature):
        Event.__init__(self, "RawReadingEvent")
        self.sensor = sensor
        self.temperature = temperature
    
    def description(self):
        return "[%s] temperature reading: sensor %d = %f" % (self.id(), self.sensor, self.temperature)

    
class Thermometer(threading.Thread):
    """ Produces raw themperature readings with no averaging of any kind """
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.active = True
        self.logger = logging.getLogger("heat.thermometer")
        self.port = serial.Serial(port = 0, baudrate = 2400)
        self.logger.info("Opened port %s" % self.port.portstr)
        
    def run(self):
        
        while (self.active):
            line = self.port.readline()
            try:
                values = line.split(' ', 2)
                sensor = int(values[0])
                temperature = float(values[1])
                event = RawReadingEvent(sensor, temperature)
                self.queue.processEvent(event)
            except:
                pass # ignore lines that cannot be parsed
        self.logger.info("Stopped")
        
    def stop(self):
        self.active = False
        self.logger.debug("Requested to stop")