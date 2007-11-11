from thermostat import HeaterStatusEvent
import os

class X10Switch:
    """ Listens for heater status events and converts them into heyu commands """
    
    def __init__(self, queue, config):
        self.subscriberId = queue.subscribe(self, "HeaterStatusEvent")
        self.queue = queue
        
    def processEvent(self, event):
        rc = os.system("heyu %s h1" % event.status);
        if rc != 0:
            raise RuntimeException("Failed to send X10 command")
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "X10 Switch"
