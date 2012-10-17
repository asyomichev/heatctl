from events.temperatureEvent import TemperatureEvent
from events.temperatureSummaryEvent import TemperatureSummaryEvent

class SensorAverage:
    def __init__(self, window, summary, currentTime):
        self.readings = []
        self.sum = 0.0
        self.lastSummary = currentTime
        self.window = window
        self.summary = summary
        
    def add(self, event):
        numReadings = len(self.readings)
        if numReadings > 1:
            oldest = self.readings[numReadings - 1]
            if event.timestamp - oldest.timestamp > self.window:
                self.readings.pop()
                self.sum -= oldest.temperature
        self.readings.insert(0, event)
        self.sum += event.temperature
        result = None
        if event.timestamp - self.lastSummary > self.summary:
            # time to generate a summary event
            result = TemperatureSummaryEvent(event.sensor, self.get(), self.window)
            self.lastSummary = event.timestamp
        return result
            
    def get(self):
        return self.sum / len(self.readings)
        
class Averager:
    """ Converts frequent raw temperature reading into less frequent running averages """
    
    def __init__(self, queue, config):
        self.subscriberId = queue.subscribe(self, "RawReadingEvent")
        self.queue = queue
        self.window = float(config.get("Control", "average"))
        self.summary = float(config.get("Control", "summary"))
        self.sensors = {}
        
    def processEvent(self, event):
        if event.sensor not in self.sensors.keys():
            self.sensors[event.sensor] = SensorAverage(self.window, self.summary, event.timestamp)
        se = self.sensors[event.sensor].add(event)
        if se: 
            self.queue.processEvent(se)
        self.queue.processEvent(TemperatureEvent(event.sensor, 
                                                 self.sensors[event.sensor].get(), 
                                                 self.window))
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Temperature Averager"
