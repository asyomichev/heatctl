import logging
import MySQLdb
import os

from events.furnaceUtilizationEvent import FurnaceUtilizationEvent

class Stats:
    """ queries the database for various stats. 
        HeaterStatusEvent is only used to trigger the query """
    
    def __init__(self, queue, config):
        self.subscriberId = queue.subscribe(self, "HeaterStatusEvent")
        self.queue = queue
        self.logger = logging.getLogger("heat.stats")
        self.window = config.get("Stats", "window")
        
        host = config.get("Database", "hostname")
        db = config.get("Database", "db")
        user = config.get("Database", "user")
        password = config.get("Database", "password")
        
        self.db = MySQLdb.connect(host, user, password, db)

    def processEvent(self, event):
        ev = FurnaceUtilizationEvent(self.getUtilization())
        self.logger.info(ev.description())
        self.queue.processEvent(ev)
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Stats"

    def status(self):
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
