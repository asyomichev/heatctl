import threading 
import logging
import serial
from events.event import Event

class RawReadingEvent(Event):
    def __init__(self, sensor, temperature):
        Event.__init__(self, "RawReadingEvent")
        self.sensor = sensor
        self.temperature = temperature
        self.current = {}
    
    def description(self):
        return "[%s] temperature reading: sensor %d = %f" % (self.id(), self.sensor, self.temperature)

    
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
        
    def status(self):
        result = 'current temperatures: \n'
        for sensor in self.current.keys():
            result += "  s%d(%s) = %f\n" % (sensor, self.names[sensor], self.current[sensor])
        return result
