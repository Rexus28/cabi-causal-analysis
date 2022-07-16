#!/bin/bash/

for MONTH in 01 02 03 04 05
do
	# echo "https://s3.amazonaws.com/capitalbikeshare-data/2022$MONTH-capitalbikeshare-tripdata.zip"
	wget "https://s3.amazonaws.com/capitalbikeshare-data/2022$MONTH-capitalbikeshare-tripdata.zip"
done

for YEAR in 18 19 20 21
do for MONTH in 01 02 03 04 05 06 07 08 09 10 11 12
do
	# echo "https://s3.amazonaws.com/capitalbikeshare-data/20$YEAR$MONTH-capitalbikeshare-tripdata.zip"
	wget "https://s3.amazonaws.com/capitalbikeshare-data/20$YEAR$MONTH-capitalbikeshare-tripdata.zip"
done
done

# specifics for the data are here https://www.ncei.noaa.gov/access
wget "https://www.ncei.noaa.gov/data/daily-summaries/access/USW00013743.csv"

