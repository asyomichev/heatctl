from thermostat import HeaterStatusEvent
import logging
import os

class X10Switch:
    """ Listens for heater status events and converts them into heyu commands """
    
    def __init__(self, queue, config):
        self.testMode = (config.get("Furnace", "testMode") == "on")
        self.x10id = config.get("Furnace", "x10id")
        self.subscriberId = queue.subscribe(self, "HeaterStatusEvent")
        self.queue = queue
        self.logger = logging.getLogger("heat.furnace")
        
    def processEvent(self, event):
        rc = 0
        if not self.testMode:
            rc = os.system("heyu %s %s" % (event.status, self.x10id));
        if rc != 0:
            raise RuntimeException("Failed to send X10 command")
        self.logger.info(event.status)
        self.lastStatus = event.status
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "X10 Switch"

    def status(self):
        return "furnace status: %s" % self.lastStatus
    