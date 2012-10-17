from event import Event

class TemperatureEvent(Event):
    def __init__(self, sensor, temperature, averagingPeriod):
        Event.__init__(self, "TemperatureEvent")
        self.sensor = sensor
        self.temperature = temperature
        self.averagingPeriod = averagingPeriod
    
    def description(self):
        return "[%s] %s averaged over last %f seconds: sensor %d = %f" % (self.id(), self.type, self.averagingPeriod, self.sensor, self.temperature)
