#! /bin/sh

# protected by password
#Xvnc :2 -desktop heat -rfbport 5902 -query localhost -geometry 640x480 -depth 16 -once -fp /usr/share/X11/fonts/misc -DisconnectClients=0 passwordFile=/root/.vncpasswd -extension XFIXES


# password-free
Xvnc :2 -desktop heat -rfbport 5902 -query localhost -geometry 640x480 -depth 16 -once -fp /usr/share/X11/fonts/misc -DisconnectClients=0 -AlwaysShared -SecurityTypes=None -extension XFIXES
