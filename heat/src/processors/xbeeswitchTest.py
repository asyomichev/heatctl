import unittest
import datetime
import time
import logging
from xbeeswitch import XbeeSwitch
from events.heaterCommandEvent import HeaterCommandEvent


class MockQueue:
    def __init__(self):
        self.expectEvent = None 
    
    def processEvent(self, event):
        print event.description()
        
    def subscribe(self, listener, flt):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class MockConfig:
    def __init__(self):
        self.sections = {}
        self.sections['XBee'] = [('port', '/dev/ttyUSB1'),('baudrate', '9600'),('destAddr', '\x18\x20'),('testMode', 'off')];

    def items(self, section):
        return self.sections[section]
    
    def get(self, section, item):
        for i in self.sections[section]:
            if i[0] == item:
                return i[1]
        raise RuntimeError('Not found: %s/%s' % (section, item))

class XbeeSwitchTest(unittest.TestCase):
    
    def setUp(self):
        self.config = MockConfig()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def testHeaterCommand(self):
        q = MockQueue()
        a = XbeeSwitch(q, self.config)
        
        time.sleep(3);
        a.processEvent(HeaterCommandEvent("on"));
        time.sleep(3);
        a.processEvent(HeaterCommandEvent("off"));
        time.sleep(3);
        a.processEvent(HeaterCommandEvent("on"));
        
if __name__ == '__main__':
    unittest.main() 
