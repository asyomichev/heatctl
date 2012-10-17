from event import Event

class HeaterStatusEvent(Event):
    def __init__(self, status):
        Event.__init__(self, "HeaterStatusEvent")
        self.status = status
    
    def description(self):
        return "[%s] Heater status : %s" % (self.id(), self.status)

