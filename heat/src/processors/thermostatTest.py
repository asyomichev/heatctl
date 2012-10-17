import unittest
import datetime
import sys
import ConfigParser
import logging
from thermostat import Thermostat
from averager import TemperatureEvent

class MockQueue:
    def __init__(self):
        self.expectEvent = None 
    
    def processEvent(self, event):
        if self.expectEvent:
            if self.expectEvent != event.status:
                raise RuntimeError("Got furnace status %s, ecpected %s" % (event.status, self.expectEvent) )
        else:
            raise RuntimeError("Unexpected event %s" % event.description())
        print event.description()
        
    def subscribe(self, listener, filter):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class ThermostatTest(unittest.TestCase):
    
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("etc/heat.conf")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testScheduleParsing(self):
        q = MockQueue()
        q.expectEvent = "off"
        a = Thermostat(q, self.config)
        for entry in a.schedule:
            print entry.toString()
        self.assert_(a.findPeriod(datetime.time(0,30)).period == "night")
        self.assert_(a.findPeriod(datetime.time(3,30)).period == "night")
        self.assert_(a.findPeriod(datetime.time(5,30)).period == "morning")
        self.assert_(a.findPeriod(datetime.time(7,30)).period == "morning")
        self.assert_(a.findPeriod(datetime.time(10,30)).period == "day")
        self.assert_(a.findPeriod(datetime.time(13,30)).period == "day")
        self.assert_(a.findPeriod(datetime.time(19,30)).period == "evening")
        self.assert_(a.findPeriod(datetime.time(22,30)).period == "night")

    def testSwitching(self):
        q = MockQueue()
        q.expectEvent = "off"
        a = Thermostat(q, self.config)

        q.expectEvent = None
        e = TemperatureEvent(1, 27, 60)
        e.timestamp = datetime.time(21, 0)
        a.processEvent(e)
        
        q.expectEvent = "on"
        e = TemperatureEvent(3, 18, 60)
        e.timestamp = datetime.time(21, 10)
        a.processEvent(e)

        q.expectEvent = None
        e = TemperatureEvent(2, 26, 60) # not the active sensor
        e.timestamp = datetime.time(21, 15)
        a.processEvent(e)

        q.expectEvent = None # still too cold
        e = TemperatureEvent(3, 19, 60)
        e.timestamp = datetime.time(21, 20)
        a.processEvent(e)

        q.expectEvent = "off"
        e = TemperatureEvent(3, 20.5, 60)
        e.timestamp = datetime.time(21, 25)
        a.processEvent(e)

        q.expectEvent = None
        e = TemperatureEvent(1, 16, 60) # not the active sensor
        e.timestamp = datetime.time(21, 15)
        a.processEvent(e)
    
        q.expectEvent = None
        e = TemperatureEvent(3, 16, 60) # not the active sensor
        e.timestamp = datetime.time(5, 20)
        a.processEvent(e)

        q.expectEvent = "on"
        e = TemperatureEvent(4, 16, 60) # not the active sensor
        e.timestamp = datetime.time(5, 20)
        a.processEvent(e)

        q.expectEvent = "off"
        e = TemperatureEvent(4, 23, 60) # not the active sensor
        e.timestamp = datetime.time(5, 40)
        a.processEvent(e)

if __name__ == '__main__':
    unittest.main() 