from event import Event

class StatusRequestEvent(Event):
    def __init__(self, target):
        Event.__init__(self, "StatusRequestEvent")
        self.target = target
    
    def description(self):
        return "[%s] Status request : %s" % (self.id(), self.target)
    
