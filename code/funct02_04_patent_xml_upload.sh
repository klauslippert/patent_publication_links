#!/bin/bash

## DB credentials
source ./db_credentials.sh

## load the filepaths of the xml
value=$(<patentfiles)

## using one core  ..  you ve to adopt this command, see 'using a function'
#for ii in ${value}
#do 
#echo $ii && cat $ii  |  sed -e 's/^M/ /' | tr -d \\\n | python parse_pat_xml.py| psql -c "\copy pat_stage.xml_data from stdin;"
#done


## using a function
function upload_one()
{
echo $1 && cat $1  |  sed -e "s/$(printf '\\\r')/ /g" | tr -d \\\n | iconv -c -t UTF-8 | sed -e "s/\\\//g" | python3 funct02_05_parse_pat_xml.py | psql -c "\copy patente.stage (data) from stdin;"
}

## and one core 
#for ii in ${value}
#do 
#upload_one $ii
#done

## using same function an multiple cores
export -f upload_one
echo "$value" | parallel -j 20 'upload_one {}'


##usefull tips
# let it run without any buffers and pipe out stdout and stderr to same file
#stdbuf -i0 -o0 -e0 ./do_xml_upload.sh &> screen_log
# get one line before (=filename) and two lines after the ERROR
#cat  screen_log | grep -B 1 -A 2 "ERROR"



#sudo umount data
