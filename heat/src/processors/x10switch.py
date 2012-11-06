import logging
import os
from events.statusEvent import StatusEvent

class X10Switch:
    """ Listens for heater status events and converts them into heyu commands """
    
    def __init__(self, queue, config):
        self.testMode = (config.get("Furnace", "testMode") == "on")
        self.x10id = config.get("Furnace", "x10id")
        self.subscriberId = queue.subscribe(self, ("HeaterCommandEvent", "StatusRequestEvent"))
        self.queue = queue
        self.logger = logging.getLogger("heat.furnace")
        self.lastStatus = "off"
        
    def processEvent(self, event):
        if ("StatusRequestEvent" == event.type) and ((self.id() == event.target) or ("*" == event.target)):
            self.queue.processEvent(StatusEvent(self.id(), self.getStatus()));
        else:
            rc = 0
            if not self.testMode:
                rc = os.system("heyu %s %s" % (event.status, self.x10id));
            if rc != 0:
                raise RuntimeError("Failed to send X10 command")
            self.logger.info(event.status)
            self.lastStatus = event.status
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "X10Switch"

    def status(self):
        return "furnace status: %s" % self.lastStatus
    