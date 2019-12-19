#!/bin/sh

wc -l scriptchek2log | read lcnt other

if [ $lcnt -gt 2017 ] ; then
   ((start=$lcnt-2015))
   echo 'downsizing ...'
   tail +$start scriptchek2log > log.txtN
   mv log.txtN scriptchek2log
fi

exit 0
