import unittest
import ConfigParser
import logging
from averager import TemperatureSummaryEvent
from thermostat import HeaterStatusEvent
from scribe import Scribe

class MockQueue:
    def __init__(self):
        pass
    
    def processEvent(self, event):
        pass
        
    def subscribe(self, listener, filter):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class ScribeTest(unittest.TestCase):
    
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("etc/heat.conf")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testReadingEvent(self):
        q = MockQueue()
        s = Scribe(q, self.config)
        e = TemperatureSummaryEvent(1, 22, 60)
        s.processEvent(e)

        e = HeaterStatusEvent("on")
        s.processEvent(e)

if __name__ == '__main__':
    unittest.main() 