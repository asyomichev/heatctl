import logging
from event import Event
import datetime
from time import strptime

class HeaterStatusEvent(Event):
    def __init__(self, status):
        Event.__init__(self, "HeaterStatusEvent")
        self.status = status
    
    def description(self):
        return "[%s] Heater status : %s" % (self.id(), self.status)

        
class ScheduleEntry:
    def __init__(self, time, period, config):
        self.time = time
        self.period = period
        pr = config.get(period, "priority")
        self.priority = int(pr[1:])
        self.target = float(config.get(period, "target"))
        
    def toString(self):
        return "%s (%s) : %d => %f" % (self.time.strftime("%H:%M"), self.period, self.priority, self.target)
        
class Thermostat:
    """ Based on incoming temperature readings generates heater on/off events """
    
    def __init__(self, queue, config):
        self.logger = logging.getLogger("heat.thermostat")
        self.subscriberId = queue.subscribe(self, "TemperatureEvent")
        self.queue = queue
        self.schedule = []
        for period in config.items("Schedule"):
            time = datetime.time(*strptime(period[1], "%H:%M")[3:5])
            entry = ScheduleEntry(time, period[0], config)
            index = 0
            while index < len(self.schedule):
                if self.schedule[index].time > time:
                    break
                index += 1
            self.schedule.insert(index, entry)
        self.heaterStatus = True
        self.heaterOff()
        
    def heaterOn(self):
        if not self.heaterStatus:
            self.queue.processEvent(HeaterStatusEvent("on"))
            self.heaterStatus = True
            self.logger.debug("furnace on")
        
    def heaterOff(self):
        if self.heaterStatus:
            self.queue.processEvent(HeaterStatusEvent("off"))
            self.heaterStatus = False
            self.logger.debug("furnace off")

    def findPeriod(self, time):
        index = len(self.schedule)
        while index > 0:
            index -= 1
            entry = self.schedule[index]
            if entry.time < time:
                return entry
        return self.schedule[-1]
    
    def processEvent(self, event):
        period = self.findPeriod(event.timestamp)
        if (event.sensor == period.priority):
           self.logger.debug("At %s sensor %d = %f - %s" % (event.timestamp.strftime("%H:%M"), event.sensor, event.temperature, period.toString()))
           if (event.temperature < period.target):
               self.heaterOn()
           else:
               self.heaterOff()
        
    def unsubscribe(self):
        self.queue.unsubscribe(self.subscriberId)
        
    def id(self):
        return "Thermostat"
