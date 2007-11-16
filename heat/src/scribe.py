import logging
import MySQLdb
from event import Event
from averager import TemperatureSummaryEvent
from thermostat import HeaterStatusEvent

class Scribe:
    """ Persist events of certain types """

    def __init__(self, queue, config):
        self.subscriberId = queue.subscribe(self, ("TemperatureSummaryEvent", "HeaterStatusEvent"))

        host = config.get("Database", "hostname")
        db = config.get("Database", "db")
        user = config.get("Database", "user")
        password = config.get("Database", "password")
        
        self.db = MySQLdb.connect(host, user, password, db)
        
        self.handlers = {}
        self.handlers["TemperatureSummaryEvent"] = self.processTemperatureSummaryEvent
        self.handlers["HeaterStatusEvent"]       = self.processStatusEvent
    
    def processTemperatureSummaryEvent(self, event, c):
        c.execute(""" INSERT INTO readings (time, sensor, temperature) VALUES ("%s", %d, %f) """ %
                  (event.getTimestamp(), event.sensor, event.temperature))

    def processStatusEvent(self, event, c):
        c.execute(""" INSERT INTO commands (time, eventType, eventData) VALUES ("%s", "%s", "%s") """ % 
                  (event.getTimestamp(), event.type, event.status))
    
    def processEvent(self, event):
        try:
            c = self.db.cursor()
            self.handlers[event.type](event, c)
            self.db.commit()
        except:
            self.db.rollback()
            raise
        
        
