from queue import EventQueue
from thermometer import Thermometer
from averager import Averager
from thermostat import Thermostat
from x10switch import X10Switch

import logging
import time
import getpass
import ConfigParser
import sys


class EventLogger:
    def __init__(self, queue, filter):
        self.subscriberId = queue.subscribe(self, filter)
        self.queue = queue
        self.logger = logging.getLogger("heat.eventlogger")
        
    def processEvent(self, event):
        self.logger.debug(event.description())
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Event Logger"


if len(sys.argv) <= 1:
    raise RuntimeError("Please specify configuration file in the first argument")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
                    #filename='/tmp/myapp.log',
                    #filemode='w')
                    
logger = logging.getLogger("heat.init")
config = ConfigParser.ConfigParser()
configFile = sys.argv[1]
logger.info("Loading configuration from %s" % configFile)
config.read(configFile)
logger.info("Creating the queue")
queue = EventQueue()
queue.start()

logger.info("Configuring components")
eventLogger = EventLogger(queue, [".*"] )
averager = Averager(queue, config)
thermometer = Thermometer(queue)
thermostat = Thermostat(queue, config)
switch = X10Switch(queue, config)
thermometer.start()

logger.info("Entering main loop")
for i in range(0, 559):
    time.sleep(1)

logger.info("Shutting down components")
thermometer.stop()
switch.unsubscribe()
thermostat.unsubscribe()
averager.unsubscribe()
eventLogger.unsubscribe()

logger.info("Stopping the queue")
queue.stop()