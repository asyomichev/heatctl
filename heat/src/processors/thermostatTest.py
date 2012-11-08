import unittest
import datetime
import time
import logging
from thermostat import Thermostat
from events.temperatureEvent import TemperatureEvent
from events.statusRequestEvent import StatusRequestEvent
from events.statusEvent import StatusEvent

class MockQueue:
    def __init__(self):
        self.expectEvent = None 
    
    def processEvent(self, event):
        if not isinstance(event, StatusEvent):
            if self.expectEvent:
                if self.expectEvent != event.status:
                    raise RuntimeError("Got furnace status %s, expected %s" % (event.status, self.expectEvent) )
            else:
                raise RuntimeError("Unexpected event %s" % event.description())
        print event.description()
        
    def subscribe(self, listener, flt):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class MockConfig:
    def __init__(self):
        self.sections = {}
        self.sections['Schedule'] = [('morning', '5:00'),('day', '9:00'),('evening', '18:00'),('night', '21:00')];
        self.sections['morning' ] = [('priority', 's2'),('target','20.0')]
        self.sections['day' ]     = [('priority', 's2'),('target','20.0')]
        self.sections['evening' ] = [('priority', 's2'),('target','20.0')]
        self.sections['night' ]   = [('priority', 's3'),('target','20.0')]
        self.sections['Furnace' ] = [('repeatCommand', '60')]

    def items(self, section):
        return self.sections[section]
    
    def get(self, section, item):
        for i in self.sections[section]:
            if i[0] == item:
                return i[1]
        raise RuntimeError('Not found: %s/%s' % (section, item))

class ThermostatTest(unittest.TestCase):
    
    def setUp(self):
        self.config = MockConfig()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testScheduleParsing(self):
        q = MockQueue()
        q.expectEvent = "off"
        a = Thermostat(q, self.config)
        
        a.processEvent(StatusRequestEvent("Thermostat"));
        
        tm = datetime.datetime(year=2012,month=1,day=1)
        tm = tm + datetime.timedelta(minutes = 30)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "night")
        tm = tm + datetime.timedelta(hours = 3)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "night")
        tm = tm + datetime.timedelta(hours = 2)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "morning")
        tm = tm + datetime.timedelta(hours = 2)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "morning")
        tm = tm + datetime.timedelta(hours = 3)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "day")
        tm = tm + datetime.timedelta(hours = 3)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "day")
        tm = tm + datetime.timedelta(hours = 5)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "evening")
        tm = tm + datetime.timedelta(hours = 3)
        self.assert_(a.findPeriod(time.mktime(tm.timetuple())).period == "night")

    def testSwitching(self):
        q = MockQueue()
        q.expectEvent = "off"
        a = Thermostat(q, self.config)

        tm = datetime.datetime(year=2012,month=1,day=1,hour=21)
        q.expectEvent = None
        e = TemperatureEvent(1, 27, 60)
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)
        
        tm = tm + datetime.timedelta(minutes = 10)
        q.expectEvent = "on"
        e = TemperatureEvent(3, 18, 60)
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        tm = tm + datetime.timedelta(minutes = 5)
        q.expectEvent = None
        e = TemperatureEvent(2, 26, 60) # not the active sensor
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        tm = tm + datetime.timedelta(minutes = 10)
        q.expectEvent = None # still too cold
        e = TemperatureEvent(3, 19, 60)
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        tm = tm + datetime.timedelta(minutes = 5)
        q.expectEvent = "off"
        e = TemperatureEvent(3, 20.5, 60)
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        tm = tm - datetime.timedelta(minutes = 10)
        q.expectEvent = None
        e = TemperatureEvent(1, 16, 60) # not the active sensor
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)
    
        tm = tm - datetime.timedelta(hours = 15, minutes = 55)
        q.expectEvent = None
        e = TemperatureEvent(3, 16, 60) # not the active sensor
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        q.expectEvent = "on"
        e = TemperatureEvent(4, 16, 60) # not the active sensor
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

        tm = tm + datetime.timedelta(minutes = 0)
        q.expectEvent = "off"
        e = TemperatureEvent(4, 23, 60) # not the active sensor
        e.timestamp = time.mktime(tm.timetuple())
        a.processEvent(e)

if __name__ == '__main__':
    unittest.main() 