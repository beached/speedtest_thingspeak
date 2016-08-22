#!/bin/bash

export API_KEY=`cat /etc/speedtest_thingspeak.key|tr -d '[[:space:]]'`

export results=`speedtest-cli --simple`
#export results="Ping: 75.92 ms
#Download: 19.40 Mbit/s
#Upload: 1.02 Mbit/s"

echo ${results}

export ping_test=`echo ${results}|cut -f2 -d' '|tr -d '[[:space:]]'`
export download_test=`echo ${results}|cut -f5 -d' '|tr -d '[[:space:]]'`
export upload_test=`echo ${results}|cut -f8 -d' '|tr -d '[[:space:]]'`

export RESULT=`wget -qO- "https://api.thingspeak.com/update?key=${API_KEY}&field1=${ping_test}&field2=${download_test}&field3=${upload_test}"`

echo "PING: ${ping_test}"
echo "DOWN: ${download_test}"
echo "UP  : ${upload_test}"
echo "RESULT: ${RESULT}"
