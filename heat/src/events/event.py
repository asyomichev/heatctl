import time

class Event:
    """ Base event class """
    def __init__(self, eventClass):
        self.timestamp = time.time()
        self.type = eventClass
        
    def id(self):
        """ String representation of the timestamp, an int with 10ms resolution """
        return "%d" % self.timestamp
    
    def getTimestamp(self):
        return str(self.timestamp)
    
    def data(self):
        """ A string representation of event-specific data """
        return ""

    def description(self):
        return "[%s] Abstract event" % self.id()
