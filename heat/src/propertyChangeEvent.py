from event import Event

class PropertyChangeEvent(Event):
    def __init__(self, name, value, replay = False):
        Event.__init__(self, "PropertyChangeEvent")
        self.name = name
        self.value = value
        self.replay = replay
    
    def description(self):
        return "[%s] property change: %s = %s" % (self.id(), self.name, self.value)
