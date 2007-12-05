#!/usr/bin/env python

import sys
from averager import TemperatureEvent
import pygtk
import gtk
import gtk.glade
import threading

class Appgui(threading.Thread):
  def __init__(self, queue, thermostat):
    threading.Thread.__init__(self)
    gladefile="../glade/toy.glade"
    windowname="heat"
    self.wTree=gtk.glade.XML (gladefile,windowname)
    
    self.temperatures = {}
    self.setCurrent(None)
    
    dic = { "on_Ok_clicked" : \
            self.ok_clicked,
            "on_serverinfo_destroy" : \
            (gtk.mainquit) }
    self.wTree.signal_autoconnect (dic)
        
    self.subscriberId = queue.subscribe(self, "TemperatureEvent")
    self.queue = queue
    self.thermostat = thermostat
    
  def unsubscribe(self):
    gtk.main_quit()
    self.queue.unsubscribe(self.subscriberId)
      
  def id(self):
    return "User Interface"
   
  def processEvent(self, event):
    pt = self.temperatures.setdefault(event.sensor, 0.0) 
    self.temperatures[event.sensor] = event.temperature
    #print pt, event.temperature
    if pt != event.temperature:
      currentSensor = self.thermostat.currentTarget().priority
      gtk.threads_enter()
      self.setCurrent(currentSensor)
      gtk.threads_leave()

  def setCurrent(self, sensor):
    for s in [1, 2, 3, 4]:
      w = self.wTree.get_widget("s%d" % s)
      w.set_alignment(1,0)
      t = self.temperatures.setdefault(s, 0.0)
      if (s != sensor):
        format = u"<span font_desc='16'>%.1f\N{DEGREE SIGN}C</span>" % t
      else:
        format = u"<b><span font_desc='28'>%.1f\N{DEGREE SIGN}C</span></b>" % t
      w.set_markup(format)

  def ok_clicked(self,widget):
    print "button clicked"
    
  def run(self):
    gtk.gdk.threads_init()
    gtk.main()


