#!/bin/bash
# Script to check if NatureWatch Camera Service has stopped responding
LOGPATH=/home/pi/NaturewatchCameraServer/helpers/watchdog.log

/bin/wget -O - -T 2 -t 1 -q http://127.0.0.1/api/settings > /dev/null
if [ $? -ne 1 ]
then
    CURDATE=$(/bin/date)
    /bin/echo "$CURDATE - NatureWatch Camera Service has hung. Trying to restart..." >>${LOGPATH}
    systemctl restart python.naturewatch.service >>${LOGPATH}
    /bin/sleep 30
    /bin/curl --request POST --url http://127.0.0.1/api/session/start/video
    /bin/echo "NatureWatch Camera Service has been restarted." >>${LOGPATH}
    /bin/echo " " >>${LOGPATH}
fi
