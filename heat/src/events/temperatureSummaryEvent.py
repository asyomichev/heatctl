from temperatureEvent import TemperatureEvent

class TemperatureSummaryEvent(TemperatureEvent):
    def __init__(self, sensor, temperature, averagingPeriod):
        TemperatureEvent.__init__(self, sensor, temperature, averagingPeriod)
        self.type = "TemperatureSummaryEvent"
    
