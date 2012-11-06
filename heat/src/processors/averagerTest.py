import unittest
import ConfigParser
import logging
from averager import Averager
from events.rawReadingEvent import RawReadingEvent

class MockQueue:
    def __init__(self):
        self.expectTemp = None 
        self.expectSum = None 
    
    def processEvent(self, event):
        if self.expectTemp and event.type == "TemperatureEvent":
            if self.expectTemp != event.temperature:
                raise RuntimeError("Wrong temperature %f, expected %f" % (event.temperature, self.expectTemp))
        elif self.expectSum and event.type == "TemperatureSummaryEvent":
            if (self.expectSum != event.temperature):
                raise RuntimeError("Wrong summary temperature %f, expected %f" % (event.temperature, self.expectTemp))
        else:
            raise RuntimeError("Unexpected event %s" % event.description())
        
    def subscribe(self, listener, filter):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class AveragerTest(unittest.TestCase):
    
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.add_section("Control")
        self.config.set("Control", "average",  "60")
        self.config.set("Control", "summary", "90")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testAveraging(self):
        q = MockQueue()
        a = Averager(q, self.config)
        q.averager = a
        
        e0 = RawReadingEvent(0, 5.0)
        e0.timestamp = 0
        q.expectTemp = 5.0
        a.processEvent(e0)
        
        e0 = RawReadingEvent(0, 8.0)
        e0.timestamp = 20
        q.expectTemp = 6.5
        a.processEvent(e0)

        e0 = RawReadingEvent(0, 2.0)
        e0.timestamp = 40
        q.expectTemp = 5.0
        a.processEvent(e0)

        e0 = RawReadingEvent(0, 14.0)
        e0.timestamp = 70
        q.expectTemp = 8.0
        a.processEvent(e0)

        e0 = RawReadingEvent(0, 8.0)
        e0.timestamp = 100
        q.expectTemp = 8.0
        q.expectSum = 8.0
        a.processEvent(e0)

        e0 = RawReadingEvent(0, 8.0)
        e0.timestamp = 100
        q.expectTemp = 8.0
        q.expectSum = None
        a.processEvent(e0)
    
    def testSummary(self):
        pass

if __name__ == '__main__':
    unittest.main() 