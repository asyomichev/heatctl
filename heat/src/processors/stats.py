import logging
import MySQLdb
import os
from events.statusEvent import StatusEvent

from events.furnaceUtilizationEvent import FurnaceUtilizationEvent

class Stats:
    """ queries the database for various stats. 
        StatusRequestEvent is only used to trigger the query """
    
    def __init__(self, queue, config):
        self.subscriberId = queue.subscribe(self, "StatusRequestEvent")
        self.queue = queue
        self.logger = logging.getLogger("heat.stats")
        self.window = config.get("Stats", "window")
        
        host = config.get("Database", "hostname")
        db = config.get("Database", "db")
        user = config.get("Database", "user")
        password = config.get("Database", "password")
        
        self.db = MySQLdb.connect(host, user, password, db)

    def processEvent(self, event):
        if ("StatusRequestEvent" == event.type) and ((self.id() == event.target) or ("*" == event.target)):
            self.queue.processEvent(StatusEvent(self.id(), self.getStatus()));
            self.queue.processEvent(FurnaceUtilizationEvent(self.getUtilization()))
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Stats"

    def getStatus(self):
        return "current furnace utilization: %d%%" % (self.getUtilization() * 100)
    
    def getUtilization(self):
        self.db.query("select count(*) from commands where time > subtime(now(), '%s') and eventData = 'on'" % self.window)
        r = self.db.store_result()
        onCount = r.fetch_row()[0][0]

        self.db.query("select count(*) from commands where time > subtime(now(), '%s') and eventData = 'off'" % self.window)
        r = self.db.store_result()
        offCount = r.fetch_row()[0][0]

        utilization = float(onCount) / float(offCount + onCount)
        return utilization
