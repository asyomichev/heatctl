import time

class Event:
    """ Base event class """
    def __init__(self, eventClass):
        self.timestamp = time.time()
        self.type = eventClass
        
    def id(self):
        """ String representation of the timestamp, an int with 10ms resolution """
        return "%d" % int(self.timestamp * 100)
    
    def getTimestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
    
    def data(self):
        """ A string representation of event-specific data """
        return ""

    def description(self):
        return "[%s] Abstract event" % self.id()
