#!/usr/bin/env python

import sys
from averager import TemperatureEvent
from stats import FurnaceUtilizationEvent
from propertyChangeEvent import *
import pygtk
import gtk
import gtk.glade
import gobject
import threading

class Appgui(threading.Thread):
  def __init__(self, queue, thermostat):
    threading.Thread.__init__(self)
    gladefile="../glade/toy.glade"
    windowname="heat"
    self.wTree = gtk.glade.XML (gladefile,windowname)
    
    self.flame = gtk.Image()
    self.flame.set_from_file("../images/flame.jpg")
    self.flame.show()

    self.noflame = gtk.Image()
    self.noflame.set_from_file("../images/noflame.jpg")
    self.noflame.show()

    self.temperatures = {}
    self.setCurrent(None)
    self.lastStatus = None
    self.setImage("off")
    
    dic = { "on_furnaceStatus_clicked" : \
            self.furnaceStatus_clicked,
            "on_target_changed" : \
            self.targetChanged,
            "on_serverinfo_destroy" : \
            (gtk.mainquit) }
    self.wTree.signal_autoconnect (dic)
        
    self.subscriberId = queue.subscribe(self, ("TemperatureEvent", "HeaterStatusEvent", "PropertyChangeEvent", "FurnaceUtilizationEvent"))
    self.queue = queue
    self.thermostat = thermostat
    
    self.sourceIds = {}
    self.blue = gtk.gdk.Color(red=128, blue=210, green=128)
    self.black = gtk.gdk.Color(red=210, blue=210, green=210)

    self.handlers = {}
    self.handlers["TemperatureEvent"] = self.processTemperatureEvent
    self.handlers["PropertyChangeEvent"] = self.processPropertyChangeEvent
    self.handlers["HeaterStatusEvent"] = self.processHeaterStatusEvent
    self.handlers["FurnaceUtilizationEvent"] = self.processFurnaceUtilizationEvent

  def unsubscribe(self):
    gtk.main_quit()
    self.queue.unsubscribe(self.subscriberId)
      
  def id(self):
    return "User Interface"
   
  def processTemperatureEvent(self, event):
    pt = self.temperatures.setdefault(event.sensor, 0.0) 
    self.temperatures[event.sensor] = event.temperature
    if pt != event.temperature:
      currentTarget = self.thermostat.currentTarget()
      self.setCurrent(currentTarget.priority)
      self.highlightTarget(currentTarget.period)

  def processHeaterStatusEvent(self, event):
    self.setImage(event.status)
      
  def processPropertyChangeEvent(self, event):
    nameParts = event.name.split('.')
    if len(nameParts) == 2 and nameParts[1] == "target":
      w = self.wTree.get_widget(nameParts[0])
      w.set_value(float(event.value))

  def processFurnaceUtilizationEvent(self, event):
    w = self.wTree.get_widget("furnaceUtilization")
    u = event.utilization * 100
    w.set_text("%d%%" % u)
      
  def processEvent(self, event):
    gtk.gdk.threads_enter()
    self.handlers[event.type](event)
    gtk.gdk.threads_leave()

  def setImage(self, status):
    w = self.wTree.get_widget("furnaceStatus")

    if self.lastStatus == True:
      w.remove(self.flame)
    elif self.lastStatus == False:
      w.remove(self.noflame)
    else:
      print "status wasn't set"

    if status == "on":
      w.add(self.flame)
      self.lastStatus = True
    else:
      w.add(self.noflame)
      self.lastStatus = False
                              
  def setCurrent(self, sensor):
    for s in [1, 2, 3, 4]:
      w = self.wTree.get_widget("s%d" % s)
      w.set_alignment(1,0)
      t = self.temperatures.setdefault(s, 0.0)
      if (s != sensor):
        format = u"<span font_desc='12'>%.1f\N{DEGREE SIGN}C</span>" % t
      else:
        format = u"<b><span font_desc='16'>%.1f\N{DEGREE SIGN}C</span></b>" % t
      w.set_markup(format)
      
  def highlightTarget(self, period):
    for p in ('morning', 'day', 'evening', 'night'):
      w = self.wTree.get_widget("lb_" + p)
      if (p == period):
        w.set_markup("<b><span foreground='red'>%s</span></b>" % p)
      else:
        w.set_markup(p)

  def furnaceStatus_clicked(self,widget):
    if self.lastStatus:
      self.setImage("off")
    else:
      self.setImage("on")
    
  def targetChanged(self, widget):
    print "-"
    if widget in self.sourceIds:
        gobject.source_remove(self.sourceIds[widget])
    #widget.modify_base(gtk.STATE_NORMAL, self.blue)
    self.sourceIds[widget] = gobject.timeout_add(3000, self.onTimeout, widget)    
    
  def onTimeout(self, widget):
      del self.sourceIds[widget]
      #widget.modify_base(gtk.STATE_NORMAL, self.black)
      event = PropertyChangeEvent(widget.get_name() + ".target", 
                                  widget.get_value())
      self.queue.processEvent(event)

    
  def run(self):
    gtk.gdk.threads_init()
    gtk.main()


