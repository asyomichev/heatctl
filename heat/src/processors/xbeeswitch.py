from events.statusEvent import StatusEvent
from xbee import XBee
import logging
import serial
import os
import time

class XbeeSwitch:
    ''' Listens for heater status events and sends them over an XBee DIO link '''
    
    def __init__(self, queue, config):
        self.testMode = (config.get('XBee', 'testMode') == 'on')
        self.logger = logging.getLogger('heat.xbee')
        self.lastStatus = 'off'
        
        # Connect the XBee lazily, from event processing thread,
        # as serial/xbee seem to lock up if accessed from different threads
        self.xbee = None
        self.config = config 

        # Subscribe to events
        self.subscriberId = queue.subscribe(self, ('HeaterCommandEvent', 'StatusRequestEvent'))
        self.queue = queue
      
    def connect(self):
        # Connect the XBee
        self.logger.debug('Initializing xbee connection...')
        confSection = 'XBee'
        port = self.config.get(confSection, 'port')
        baudrate = self.config.get(confSection, 'baudrate')
        tty = serial.Serial(port, baudrate)
        self.xbee = XBee(tty)
        self.xbee.send('at', frame_id='A', command='MY')
        self.myid = self.xbee.wait_read_frame()
        self.dest = self.config.get(confSection, 'destAddr').decode('string_escape')
        self.logger.debug('Local XBee: %s, remote: %s' % (self.myid, self.dest))

        # Flex the muscules
        self.sendCommand('on')
        time.sleep(3)
        self.sendCommand('off')

        
    def sendCommand(self, onoff):
        if not self.xbee:
            self.connect() # lazy initialization

        param = '\x01' if onoff == 'on' else '\x00'
        self.logger.debug('About to send command "%s"' % onoff)
        self.xbee.send('remote_at', frame_id='A', dest_addr=self.dest, command='IO', parameter=param)
        self.logger.debug('Sent command "%s", response: "%s"' % (onoff, self.xbee.wait_read_frame()))
        
    def processEvent(self, event):
        if ('StatusRequestEvent' == event.type) and ((self.id() == event.target) or ('*' == event.target)):
            self.queue.processEvent(StatusEvent(self.id(), self.getStatus()));
        else:
            if not self.testMode:
                self.sendCommand(event.status);
            self.logger.info(event.status + ('(test mode)' if self.testMode else ''))
            self.lastStatus = event.status
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return 'XbeeSwitch'

    def status(self):
        return 'XBee last command: %s' % self.lastStatus
    
