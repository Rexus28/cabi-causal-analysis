#!/bin/bash/

# download the data
# echo "downloading the data"
# cd data
# bash get_data.sh
# cd ..

python src/create_dataset.py --bike_dir data/ --wx_file data/USW00013743.csv\
 --output results/capitalbikeshare-weather-201801-202205.csv

