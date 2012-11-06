from event import Event

class RawReadingEvent(Event):
    def __init__(self, sensor, temperature):
        Event.__init__(self, "RawReadingEvent")
        self.sensor = sensor
        self.temperature = temperature
        self.current = {}
    
    def description(self):
        return "[%s] temperature reading: sensor %d = %f" % (self.id(), self.sensor, self.temperature)
