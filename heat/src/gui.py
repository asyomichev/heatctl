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
#            "on_s1_changed" : \
#            self.s1_changed,
            "on_serverinfo_destroy" : \
            (gtk.mainquit) }
    self.wTree.signal_autoconnect (dic)
        
    self.subscriberId = queue.subscribe(self, ("TemperatureEvent", "HeaterStatusEvent", "PropertyChangeEvent"))
    self.queue = queue
    self.thermostat = thermostat
    
  def unsubscribe(self):
    gtk.main_quit()
    self.queue.unsubscribe(self.subscriberId)
      
  def id(self):
    return "User Interface"
   
  def processEvent(self, event):
    gtk.gdk.threads_enter()
    
    if event.type == "TemperatureEvent":
      pt = self.temperatures.setdefault(event.sensor, 0.0) 
      self.temperatures[event.sensor] = event.temperature
      #print pt, event.temperature
      if pt != event.temperature:
        currentTarget = self.thermostat.currentTarget()
        self.setCurrent(currentTarget.priority)
        self.highlightTarget(currentTarget.period)
        
    elif event.type == "HeaterStatusEvent":
      self.setImage(event.status)
      
    elif event.type == "PropertyChangeEvent":
      nameParts = event.name.split('.')
      if len(nameParts) == 2 and nameParts[1] == "target":
        w = self.wTree.get_widget(nameParts[0])
        w.set_value(float(event.value))
        
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
        format = u"<span font_desc='16'>%.1f\N{DEGREE SIGN}C</span>" % t
      else:
        format = u"<b><span font_desc='28'>%.1f\N{DEGREE SIGN}C</span></b>" % t
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
    
  def target_changed(self, widget):
    print "-"
    print widget.get_value()
    
  def run(self):
    gtk.gdk.threads_init()
    gtk.main()


