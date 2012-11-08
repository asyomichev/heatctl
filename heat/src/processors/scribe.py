import logging
import MySQLdb
from events.event import Event
from averager import TemperatureSummaryEvent
from events.heaterCommandEvent import HeaterCommandEvent
from events.propertyChangeEvent import PropertyChangeEvent

class Scribe:
    """ Persist events of certain types """

    def __init__(self, queue, config):

        host = config.get("Database", "hostname")
        db = config.get("Database", "db")
        user = config.get("Database", "user")
        password = config.get("Database", "password")
        
        self.db = MySQLdb.connect(host, user, password, db)

        self.queue = queue
        self.handlers = {}
        self.handlers["TemperatureSummaryEvent"] = self.processTemperatureSummaryEvent
        self.handlers["HeaterStatusEvent"]       = self.processStatusEvent
        self.handlers["PropertyChangeEvent"]     = self.processPropertyChangeEvent
        self.subscriberId = queue.subscribe(self, ("TemperatureSummaryEvent", "HeaterStatusEvent", "PropertyChangeEvent"))
        
    def processTemperatureSummaryEvent(self, event, c):
        c.execute(""" INSERT INTO readings (time, sensor, temperature) VALUES ("%s", %d, %f) """ %
                  (event.getTimestamp(), event.sensor, event.temperature))

    def processStatusEvent(self, event, c):
        c.execute(""" INSERT INTO commands (time, eventType, eventData) VALUES ("%s", "%s", "%s") """ % 
                  (event.getTimestamp(), event.type, event.status))

    def processPropertyChangeEvent(self, event, c):
        if not event.replay:
            c.execute(""" INSERT INTO properties (propertyName, lastUpdated, propertyValue) VALUES ("%s", "%s", "%s") """ % 
                      (event.name, event.getTimestamp(), event.value))
    
    def processEvent(self, event):
        try:
            c = self.db.cursor()
            self.handlers[event.type](event, c)
            self.db.commit()
        except:
            self.db.rollback()
            raise
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Scribe"
