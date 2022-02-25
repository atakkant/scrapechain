#!/bin/bash
#get the start date and time
start_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${start_datetime} - starting spider ${SPIDER_NAME}"

cd /home/atakantuncer/Desktop/certik/scrapy_env/bin
source activate

# goto to spider directory
cd #SPIDER_PATH

export LC_ALL=en_US.utf-8

curl http://localhost:6800/schedule.json -d project=$SPIDER_PROJECT -d spider=$SPIDER_NAME

#get enddate and time
end_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${end_datetime} - spider finished successfully"
echo " ------- "




