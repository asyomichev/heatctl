#!/usr/bin/env python

import sys
from averager import TemperatureEvent

#now we have both gtk and gtk.glade imported
#Also, we know we are running GTK v2

class appgui:
  def __init__(self):
    """
    In this init we are going to display the main
    serverinfo window
    """
    gladefile="../glade/toy.glade"
    windowname="heat"
    self.wTree=gtk.glade.XML (gladefile,windowname)
#    for s in ["spacer1"]:
#      w = self.wTree.get_widget(s)
#      w.set_markup("<span font_desc='32'>|</span>")

    self.temperatures = [0.0, 0.0, 0.0, 0.0]
    self.setCurrent(None)
    # we only have two callbacks to register, but
    # you could register any number, or use a
    # special class that automatically
    # registers all callbacks. If you wanted to pass
    # an argument, you would use a tuple like this:
    # dic = { "on button1_clicked" : \
    #         (self.button1_clicked, arg1,arg2) , ...

    dic = { "on_Ok_clicked" : \
            self.ok_clicked,
            "on_serverinfo_destroy" : \
            (gtk.mainquit) }
    self.wTree.signal_autoconnect (dic)
    return

  def setCurrent(self, sensor):
    for s in [1, 2, 3, 4]:
      w = self.wTree.get_widget("s%d" % s)
      w.set_alignment(1,0)
      if (s != sensor):
        format = u"<span font_desc='16'>%.1f\N{DEGREE SIGN}C</span>" % self.temperatures[s - 1]
      else:
        format = u"<b><span font_desc='28'>%.1f\N{DEGREE SIGN}C</span></b>" % self.temperatures[s - 1]
      w.set_markup(format)

#####CALLBACKS
  def ok_clicked(self,widget):
    print "button clicked"

try:
  import pygtk
  #tell pyGTK, if possible, that we want GTKv2
  pygtk.require("2.0")
except:
  print "pygtk requires GTKv2"
  #Some distributions come with GTK2, but not pyGTK
  pass

try:
  import gtk
  import gtk.glade
except:
  print "You need to install pyGTK or GTKv2 ",
  print "or set your PYTHONPATH correctly."
  print "try: export PYTHONPATH=",
  print "/usr/local/lib/python2.2/site-packages/"
  sys.exit(1)

# we start the app like this...
app=appgui()
app.setCurrent(0)
gtk.main()

