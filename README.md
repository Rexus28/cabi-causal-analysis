# Causal Analysis of Capital Bikeshare and Weather Data
## Overview
Interested in looking at the effects of weather on biking, specifically using the Capital Bikeshare rider data from the DC metro area. The goals for this project are to create a dashboard for exploring the data and understanding what it tells us about ridership in different weather conditions on a daily basis. The next part of this project is to assess the causal effect that weather was on the ridership via DoWhy + EconML, and compare the results to linear regression analysis.

I was partial inspired the UCI [Bike Sharing Dataset Data Set](https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset), but collecting more recent data on my own.


## Getting the data
The Capital Bikeshare data is easily accessible via their online [system data portal](https://ride.capitalbikeshare.com/system-data). Which I found through a [Bike Share Data Systems GitHub](https://github.com/BetaNYC/Bike-Share-Data-Best-Practices/wiki/Bike-Share-Data-Systems).

The weather data on the other hand is a little more difficult. The most straightforward approach is to use the [NCEI Access Portal](https://www.ncei.noaa.gov/access) from NOAA. This offers only basic information, but it's quick and easy to get some weather data. I'm also looking into getting more detailed information from the [NCDC Climate Data Online Search](https://www.ncdc.noaa.gov/cdo-web/search) from NOAA, but you have to be specific about the dates and type of data you want. You also need to request the data and are limited in the total time length of data you can request. For documentation on the weather data, check out this [link](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt).

To get the data run the script in the `/data/` directory:
```
$ cd data
$ bash get_data.sh
```

## Merging and preparing the data
Bike ridership data is aggregated to the daily level, summing total rides and rides by bike and rider type. This is joined with the cleaned daily summary weather data by date and stored in the `/results/` directory. To create the dataset from the downloaded data run the `create_dataset.py` script:
```
$ python src/create_dataset.py --bike_dir data/ --wx_file data/USW00013743.csv --output results/capitalbikeshare-weather-201801-202205.csv
```
