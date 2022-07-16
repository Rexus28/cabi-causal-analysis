#!python3

import os
import argparse
import pandas as pd
from process_data import create_ridership_dataframe
from process_data import read_weather_data


def create_dataset(bike_dir="/data", wx_file="/data/USW00013743.csv",
                   output_file="/results/capitalbikeshare-weather.csv"):
    bike_df = create_ridership_dataframe(bike_dir)

    wx_df = read_weather_data(wx_file)
    wx_df = wx_df.rename(columns={"DATE": "date"})

    merged_df = pd.merge(bike_df, wx_df, left_on="date", right_on="date", how="left")
    output_dir = os.path.basename(output_file)
    os.makedirs(output_dir, exist_ok=True)
    merged_df.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bike_dir", type=str, required=True,
                        help="directory with zip files for the bikeshare data")
    parser.add_argument("--wx_file", type=str, required=True,
                        help="path to the weather data")
    parser.add_argument("--output", type=str, required=True,
                        help="path for the output file")
    args = parser.parse_args()
    create_dataset(args.bike_dir, args.wx_file, args.output)
    print("Done!")
    