#!/bin/bash 


/usr/bin/ps axu |grep sust |awk '{print $2}' |xargs kill -9  &>/dev/null &
 
/usr/bin/ps axu |grep worker |awk '{print $2}' |xargs kill -9   &>/dev/null &

/usr/bin/ps axu |grep uwsgi |awk '{print $2}' |xargs kill -9   &>/dev/null &

/usr/bin/ps axu |grep flower |awk '{print $2}' |xargs kill -9   &>/dev/null &
