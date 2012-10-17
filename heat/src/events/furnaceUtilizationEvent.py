from event import Event

class FurnaceUtilizationEvent(Event):
    def __init__(self, utilization):
        Event.__init__(self, "FurnaceUtilizationEvent")
        self.utilization = utilization
    
    def description(self):
        return "[%s] Furnace utilization %d%%" % (self.id(), self.utilization * 100)

