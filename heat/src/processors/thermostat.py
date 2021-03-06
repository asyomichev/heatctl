import logging
from events.heaterCommandEvent import HeaterCommandEvent
from events.statusEvent import StatusEvent
import datetime
import time
        
class ScheduleEntry:
    def __init__(self, time, period, config):
        self.time = time
        self.period = period
        sensorName = config.get(period, "sensor")
        self.sensorIndex = int(config.get(sensorName, "index"))
        self.target = float(config.get(period, "target"))
        
    def __str__(self):
        return "%s (%s) : %d => %f" % (self.time.strftime("%H:%M"), self.period, self.sensorIndex, self.target)
        
class Thermostat:
    """ Based on incoming temperature readings generates heater on/off events """
    
    def __init__(self, queue, config):
        self.logger = logging.getLogger("heat.thermostat")
        self.wait = float(config.get("Furnace", "repeatCommand"))
        self.lastStatusChange = 0.0
        self.handlers = {}
        self.handlers["TemperatureEvent"] = self.processTemperatureEvent
        self.handlers["PropertyChangeEvent"] = self.processPropertyChangeEvent
        self.handlers["StatusRequestEvent"] = self.processStatusRequestEvent
        self.subscriberId = queue.subscribe(self, ("TemperatureEvent", "PropertyChangeEvent", "StatusRequestEvent"))
        self.queue = queue
        self.schedule = []
        for period in config.items("Schedule"):
            tm = datetime.time(*time.strptime(period[1], "%H:%M")[3:5])
            entry = ScheduleEntry(tm, period[0], config)
            index = 0
            while index < len(self.schedule):
                if self.schedule[index].time > tm:
                    break
                index += 1
            self.schedule.insert(index, entry)
        self.heaterStatus = True
        self.heaterOff()
        
        for entry in self.schedule:
            self.logger.debug(entry.__str__())
        
    def okToRepeat(self):
        return (time.time() - self.lastStatusChange) > self.wait
    
    def heaterOn(self):
        if not self.heaterStatus or self.okToRepeat():
            self.queue.processEvent(HeaterCommandEvent("on"))
            self.heaterStatus = True
            self.lastStatusChange = time.time()
        
    def heaterOff(self):
        if self.heaterStatus or self.okToRepeat():
            self.queue.processEvent(HeaterCommandEvent("off"))
            self.heaterStatus = False
            self.lastStatusChange = time.time()
            
    def getStatus(self):
        result = ''
        for s in self.schedule:
            result += '\n    %s' % s
        result += "\nCurrent target: %s, last command sent %ds ago" % (self.currentTarget(), time.time() - self.lastStatusChange)
        return result

    def findPeriod(self, timestamp):
        index = len(self.schedule)
        timeofday = datetime.datetime.fromtimestamp(timestamp).time()
        while index > 0:
            index -= 1
            entry = self.schedule[index]
            if entry.time < timeofday:
                return entry
        return self.schedule[-1]
    
    def processTemperatureEvent(self, event):
        period = self.findPeriod(event.timestamp)
        self.logger.debug("Sensor %d = %f, current period %s" % (event.sensor, event.temperature, period.__str__()))
        if (event.sensor == period.sensorIndex):
            if event.temperature < (period.target * 0.98):
                self.heaterOn()
            elif event.temperature > (period.target * 1.02):
                self.heaterOff()
    
    def processPropertyChangeEvent(self, event):
        nameParts = event.name.split('.')
        if len(nameParts) == 2 and nameParts[1] == "target":
            for entry in self.schedule:
                if entry.period == nameParts[0]:
                    entry.target = float(event.value)
                    self.logger.info("Target temperature for %s is set to %f" % 
                                     (entry.period, entry.target))

    def processStatusRequestEvent(self, event):
        if (self.id() == event.target or "*" == event.target):
            self.queue.processEvent(StatusEvent(self.id(), self.getStatus()));    
    
    def processEvent(self, event):
        self.handlers[event.type](event)
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Thermostat"

    def timeNow(self):
        return time.time() 

    def currentTarget(self):
        return self.findPeriod(self.timeNow())
    
