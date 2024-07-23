#!/bin/bash
# Script to check if NatureWatch Camera Service has stopped responding
LOGPATH=/home/pi/NaturewatchCameraServer/helpers/watchdog.log
LAST_CAPTURE_MODE=UNSET

# Sleeping for 5 minutes when the script starts to give the service time to run at boot
/bin/sleep 300

while true
do
    RESPONSE=`/bin/wget -O - -T 2 -t 1 -q http://127.0.0.1/api/settings` > /dev/null
    if [ $? -eq 0 ];then
        # Service is working so we store the current capture mode
        CAPTURE_MODE=`/bin/echo ${RESPONSE}|/bin/awk -F "," '{print $12}'` > /dev/null
        if [[ $CAPTURE_MODE == *"inactive"* ]];then
            # Capture mode is inactive
            LAST_CAPTURE_MODE=INACTIVE
        elif [[ $CAPTURE_MODE == *"photo"* ]];then
            # Capture mode is set to "photo"
            LAST_CAPTURE_MODE=PHOTO
        elif [[ $CAPTURE_MODE == *"video"* ]];then
            # Capture mode is set to "video"
            LAST_CAPTURE_MODE=VIDEO
        elif [[ $CAPTURE_MODE == *"timelapse"* ]];then
            # Capture mode is set to "timelapse"
            LAST_CAPTURE_MODE=TIMELAPSE
        fi
    else
        # Capture mode is either not working or the settings are being changed. Trying again just in case...
        /bin/sleep 3
        /bin/wget -O - -T 2 -t 1 -q http://127.0.0.1/api/settings > /dev/null
        if [ $? -ne 0 ];then
            # After two checks the service has failed so we need to restart services
            CURDATE=$(/bin/date)
            /bin/echo "$CURDATE - NatureWatch Camera Service has hung. Trying to restart..." >>${LOGPATH}
            systemctl restart python.naturewatch.service >>${LOGPATH}
            /bin/sleep 30
            # Restarting last capture mode
            if [[ $LAST_CAPTURE_MODE == "PHOTO" ]];then
                /bin/curl --request POST --url http://127.0.0.1/api/session/start/photo > /dev/null 2>&1
            elif [[ $LAST_CAPTURE_MODE == "VIDEO" ]];then
                /bin/curl --request POST --url http://127.0.0.1/api/session/start/video > /dev/null 2>&1
            elif [[ $LAST_CAPTURE_MODE == "TIMELAPSE" ]];then
                /bin/curl --request POST --url http://127.0.0.1/api/session/start/timelapse > /dev/null 2>&1
            fi
            /bin/echo "NatureWatch Camera Service has been restarted." >>${LOGPATH}
            /bin/echo " " >>${LOGPATH}
        fi
    fi
    # Wait another 5 minutes before we check again
    /bin/sleep 300
done