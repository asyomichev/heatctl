from thermostat import ScheduleEntry
from gui import Appgui

class MockQueue:
    def __init__(self):
        self.expectTemp = None 
        self.expectSum = None 
    
    def processEvent(self, event):
        if self.expectTemp and event.type == "TemperatureEvent":
            if self.expectTemp != event.temperature:
                raise RuntimeError("Wrong temperature %f, expected %f" % (event.temperature, self.expectTemp))
        elif self.expectSum and event.type == "TemperatureSummaryEvent":
            if (self.expectSum != event.temperature):
                raise RuntimeError("Wrong summary temperature %f, expected %f" % (event.temperature, self.expectTemp))
        else:
            raise RuntimeError("Unexpected event %s" % event.description())
        
    def subscribe(self, listener, filter):
        pass
        
    def unsubscribe(self, listenerId):
        pass

class MockThermostat():
  def  currentTarget(self): 
    e = thermostat.ScheduleEntry(0, 0, 0)
    e.priority = 1
    return e

def main():
  queue = MockQueue()
  thermostat = MockThermostat()
  gui = Appgui(queue, thermostat)
  gui.run()

if __name__ == '__main__':
    main() 