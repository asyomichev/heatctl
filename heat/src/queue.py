import threading
import logging
import re
    
class Subscription:
    """ A subscription table entry """
    def __init__(self, subscriber, filters, logger):
        self.logger = logger
        self.subscriber = subscriber
        self.filters = []
        for fe in filters:
            self.filters.append(re.compile(fe))
    
    def processEvent(self, event):
        for fp in self.filters:
            if fp.match(event.type):
                try:
                    self.subscriber.processEvent(event)
                except:
                    self.logger.error("%s failed to process event %s" % (self.subscriber.id(), event.description()))
                return
    
class EventQueue(threading.Thread):
    """ Global event queue, implements Listener interface so that it can accept new events """
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = []
        self.subscriptions = {}
        self.active = True
        self.mutex = threading.Lock()
        self.condition = threading.Condition(self.mutex)
        self.logger = logging.getLogger("heat.eventqueue")
        self.logger.info("Created")
        
    def run(self):
        """ Main event processing loop """
        self.logger.info("Started")
        self.mutex.acquire()
        while self.active:
            while len(self.queue) > 0:
                event = self.queue.pop(0)
                self.mutex.release()
                self.notifyListeners(event)
                self.mutex.acquire()
            self.condition.wait()
        self.mutex.release()
        self.logger.info("Stopped")
            
    def stop(self):
        self.logger.debug("Requested to stop")        
        self.mutex.acquire()
        self.active = False
        self.condition.notify()
        self.mutex.release()
        self.join()
    
    def processEvent(self, event):
        """ Accept and enqueue an incoming event """
        self.mutex.acquire()
        self.queue.append(event)
        queueSize = len(self.queue)
        self.condition.notify()
        self.mutex.release()
        self.logger.debug("{%d} + %s" % (queueSize, event.description()))

    def notifyListeners(self, event):
        for subscription in self.subscriptions.values():
            subscription.processEvent(event)
    
    def subscribe(self, listener, filter):
        """ Enter the given subscriber into the event distribution list """
        listenerId = len(self.subscriptions)
        self.subscriptions[listenerId] = Subscription(listener, filter, self.logger)
        self.logger.debug("New listener %s (id: %d)" % (listener.id(), listenerId))
        return listenerId
        
    def unsubscribe(self, listenerId):
        del self.subscriptions[listenerId]
        self.logger.debug("Removed listener (id: %d)" % listenerId)
        
    def reportStatus(self, stream):
        print >> stream, "Queue status:"
        print >> stream, " subscribers: %d" % len(self.subscriptions) 
        