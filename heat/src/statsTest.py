import unittest
import ConfigParser
import logging
from thermostat import HeaterStatusEvent
from stats import Stats

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
        self.config.read("../etc/heat.conf")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testReadingEvent(self):
        q = MockQueue()
        s = Stats(q, self.config)
        e = HeaterStatusEvent("on")
        s.processEvent(e)

if __name__ == '__main__':
    unittest.main() 
