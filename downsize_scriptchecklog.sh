#!/bin/sh

wc -l scriptcheklog | read lcnt other

if [ $lcnt -gt 2017 ] ; then
   ((start=$lcnt-2015))
   echo 'downsizing ...'
   tail +$start scriptcheklog > log.txtN
   mv log.txtN scriptcheklog
fi

exit 0
