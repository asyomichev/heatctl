from event import Event

class HeaterCommandEvent(Event):
    def __init__(self, status):
        Event.__init__(self, "HeaterCommandEvent")
        self.status = status
    
    def description(self):
        return "[%s] Heater command : %s" % (self.id(), self.status)

