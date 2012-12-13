from events.statusEvent import StatusEvent
from xbee import XBee
import logging
import serial
import os
import time
import threading

class XbeeSwitch:
    ''' Listens for heater status events and sends them over an XBee DIO link '''
    
    def __init__(self, queue, config):
        self.testMode = (config.get('XBee', 'testMode') == 'on')
        self.timeout  = float(config.get('XBee', 'commandTimeout'))
        self.retry  = int(config.get('XBee', 'commandRetry'))
        self.logger = logging.getLogger('heat.xbee')
        self.lastStatus = 'off'
        self.frameId = '\x01'
        self.framesResponded = {}
        self.cond = threading.Condition()
        
        # Connect the XBee lazily, from event processing thread,
        # as serial/xbee seem to lock up if accessed from different threads
        self.xbee = None
        self.tty = None
        self.config = config 

        # Subscribe to events
        self.subscriberId = queue.subscribe(self, ('HeaterCommandEvent', 'StatusRequestEvent'))
        self.queue = queue

    def stop(self):
        if (self.xbee):
            self.xbee.halt()
            self.tty.close()
      
    def __del__(self):
        self.stop()

    def commandResponse(self, response):
        self.logger.debug('Command response: "%s"' % response)
        # e.g. {'status': '\x00', 'source_addr': '\x18 ', 'source_addr_long': '\x00\x13\xa2\x00@{5\xac', 'frame_id': 'A', 'command': 'IO', 'id': 'remote_at_response'}
        self.cond.acquire();
        try:
            self.framesResponded[response['frame_id']] = response['status']
            self.cond.notify()
        finally:
            self.cond.release()
        
    def waitCommandResponse(self, frameId):
        result = None
        started = time.time()
        self.cond.acquire()
        try:
            while (not frameId in self.framesResponded.keys() and ((time.time() - started) < self.timeout)):
                self.cond.wait(self.timeout)
        finally:
            self.cond.release()
        if (frameId in self.framesResponded):
            result = self.framesResponded.pop(frameId)
        else:
            self.logger.warn('Wait for frame %d timed out after %f seconds' % (ord(frameId), time.time() - started))
        return result
        
    def connect(self):
        # Connect the XBee
        self.logger.debug('Initializing xbee connection...')
        confSection = 'XBee'
        port = self.config.get(confSection, 'port')
        baudrate = self.config.get(confSection, 'baudrate')
        self.tty = serial.Serial(port, baudrate)
        self.xbee = XBee(self.tty, callback=lambda response: self.commandResponse(response))
        self.xbee.send('at', frame_id='A', command='MY')
        self.waitCommandResponse('A')
        self.dest = self.config.get(confSection, 'destAddr').decode('string_escape')

        # Flex the muscules
        self.sendCommand('on')
        time.sleep(3)
        self.sendCommand('off')

    def sendCommand(self, onoff):
        if not self.xbee:
            self.connect() # lazy initialization

        param = '\x01' if onoff == 'on' else '\x00'
        self.logger.debug('About to send command "%s"' % onoff)
        status = None
        retries = 0
        while (not status == '\x00' and retries < self.retry):
            self.xbee.send('remote_at', frame_id=self.frameId, dest_addr=self.dest, command='IO', parameter=param)
            status = self.waitCommandResponse(self.frameId)
            retries += 1
        self.frameId = chr(ord(self.frameId) + 1) if ord(self.frameId) < 128 else '\x01'
        if (status == '\x00'):
            self.logger.debug('Sent command "%s"' % onoff)
        else:
            self.logger.error('Command %s: failed %d attempts' % (onoff, retries))
        
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
    
