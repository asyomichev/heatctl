from events.statusEvent import StatusEvent
from xbee import XBee
import logging
import serial
import os

class XbeeSwitch:
    ''' Listens for heater status events and sends them over an XBee DIO link '''
    
    def __init__(self, queue, config):
        self.testMode = (config.get('XBee', 'testMode') == 'on')
        self.logger = logging.getLogger('heat.xbee')
        self.lastStatus = 'off'
        
        # Connect the XBee
        confSection = 'XBee'
        port = config.get(confSection, 'port')
        baudrate = config.get(confSection, 'baudrate')
        tty = serial.Serial(port, baudrate)
        self.xbee = XBee(tty)
        self.xbee.send('at', frame_id='A', command='MY')
        self.dest = config.get(confSection, 'destAddr').decode('string_escape')
        self.myid = self.xbee.wait_read_frame()
        self.logger.debug('Local XBee: 0x%02X%02X, remote: 0x%02X%02X' % (self.myid[0], self.myid[1], self.dest[0], self.dest[1]))

        # Subscribe to events
        self.subscriberId = queue.subscribe(self, ('HeaterCommandEvent', 'StatusRequestEvent'))
        self.queue = queue
        
    def sendCommand(self, onoff):
        param = '\x01' if onoff == 'on' else '\x00'
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
    