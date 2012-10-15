#!/bin/sh
SELF=`readlink -f $0`
SFD=`dirname $SELF`
cd $SFD/src
nohup python main.py ../etc/heat.conf -d >../log/heat.out 2>&1 &
 
