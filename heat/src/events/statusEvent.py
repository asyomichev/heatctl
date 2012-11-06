from event import Event

class StatusEvent(Event):
    def __init__(self, source, status):
        Event.__init__(self, "StatusEvent")
        self.source = source
        self.status = status
    
    def description(self):
        return "[%s] Status of %s : %s" % (self.id(), self.source, self.status)
    
