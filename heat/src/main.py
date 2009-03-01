from queue import EventQueue
from thermometer import Thermometer
from averager import Averager
from thermostat import Thermostat
from x10switch import X10Switch
from scribe import Scribe
from stats import Stats
from propertyReader import readProperties
from propertyChangeEvent import *
from gui import Appgui

import logging
import logging.config
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

configFile = sys.argv[1]

#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
#                    #filename='/tmp/myapp.log',
#                    #filemode='w')
logging.config.fileConfig(configFile)

logger = logging.getLogger("heat.init")
config = ConfigParser.ConfigParser()
logger.info("Loading configuration from %s" % configFile)
config.read(configFile)
logger.info("Creating the queue")
queue = EventQueue()

logger.info("Configuring components")
eventLogger = EventLogger(queue, [".*"] )
averager = Averager(queue, config)
thermometer = Thermometer(queue, config)
thermostat = Thermostat(queue, config)
switch = X10Switch(queue, config)
scribe = Scribe(queue, config)
stats = Stats(queue, config)
thermometer.start()
gui = Appgui(queue, thermostat)

# All subscribers are ready. Now we can read the latest property values
readProperties(scribe.db, queue)


gui.start()
queue.start()

# If started in the daemon mode, just go to endless sleep
if len(sys.argv) > 2 and sys.argv[2] == "-d":
    while True:
      time.sleep(60)

# Enter the interactive loop
cmd = ""
while cmd != "exit":
    cmdParts = raw_input("heat> ").split(' ')
    cmd = cmdParts[0]
    print cmd, cmdParts
    if (cmd == "status"):
        print queue.status()
        print switch.status()
        print thermometer.status()
        print thermostat.status()
        print stats.status()
    elif (cmd == "target"):
        period = cmdParts[1]
        if period == "now":
            period = thermostat.currentTarget().period
        event = PropertyChangeEvent(period + ".target", cmdParts[2])
        queue.processEvent(event)

logger.info("Shutting down components")
gui.unsubscribe()
scribe.unsubscribe()
thermometer.stop()
switch.unsubscribe()
thermostat.unsubscribe()
averager.unsubscribe()
eventLogger.unsubscribe()
stats.unsubscribe()

logger.info("Stopping the queue")
queue.stop()
