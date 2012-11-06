import threading 
import logging
import serial
from events.rawReadingEvent import RawReadingEvent
from events.statusEvent import StatusEvent

class Thermometer(threading.Thread):
    """ Produces raw themperature readings with no averaging of any kind """
    
    def __init__(self, queue, config):
        threading.Thread.__init__(self)
        self.queue = queue
        self.active = True
        self.logger = logging.getLogger("heat.thermometer")
        self.port = serial.Serial('/dev/ttyUSB0', baudrate = 2400)
        self.logger.info("Opened port %s" % self.port.portstr)

        self.current = {}
        self.names = {}
        for sensorName in config.items("SensorNames"):
            sensor = int(sensorName[0][1:])
            self.current[sensor] = 0.0
            self.names[sensor] = sensorName[1]
            
        self.subscriberId = queue.subscribe(self, ("StatusRequestEvent"))
        self.queue = queue
        
    def run(self):
        
        while (self.active):
            line = self.port.readline()
            try:
                values = line.split(' ', 2)
                sensor = int(values[0])
                temperature = float(values[1])
                self.current[sensor] = temperature
                event = RawReadingEvent(sensor, temperature)
                self.queue.processEvent(event)
            except:
                pass # ignore lines that cannot be parsed
        self.logger.info("Stopped")
        
    def stop(self):
        self.active = False
        self.logger.debug("Requested to stop")
        
    def id(self):
        return "Thermometer"
        
    def processEvent(self, event):
        if ("StatusRequestEvent" == event.type) and ((self.id() == event.target) or ("*" == event.target)):
            self.queue.processEvent(StatusEvent(self.id(), self.getStatus()));
        
    def getStatus(self):
        result = 'current temperatures: \n'
        for sensor in self.current.keys():
            result += "  s%d(%s) = %f\n" % (sensor, self.names[sensor], self.current[sensor])
        return result
