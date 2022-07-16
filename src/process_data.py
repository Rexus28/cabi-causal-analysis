#!python3

import os
import glob
import zipfile
import pandas as pd


def load_ride_data_zip(zip_path):
    assert os.path.exists(zip_path)
    zf = zipfile.ZipFile(zip_path) 
    # file_name = os.path.basename(os.path.splitext(zip_path)[0])
    file_name = zf.filelist[0].filename
    print(file_name)
    try:
        df = pd.read_csv(zf.open(file_name),
                         parse_dates=["started_at", "ended_at"])
        # lat long data is not needed, and not present in same files,
        # so we can remove them now
        df = df.drop(columns=["start_lat", "start_lng", "end_lat", "end_lng"])
    except ValueError:
        df = pd.read_csv(zf.open(file_name),
                         parse_dates=["Start date", "End date"])
        # older files have a difference naming convention, so update it here
        df = df.rename({"Member": "member", "Casual": "casual"})
        df = df.rename(columns={"Start date": "started_at",
                                "End date": "ended_at",
                                "Start station number": "start_station_id",
                                "Start station": "start_station_name",
                                "End station number": "end_station_id",
                                "End station": "end_station_name",
                                "Bike number": "ride_id",
                                "Member type": "member_casual"})
        df = df.drop(columns=["Duration"])
    if "rideable_type" not in df.columns:
        df["rideable_type"] = "classic_bike"
    return df


def aggregate_daily_ride_data(df):
    day_df = (
        df
        # .drop(columns=["start_lat", "start_lng", "end_lat", "end_lng"])
        # .loc[lambda df: df["rideable_type"] != "docked_bike"]
        .assign(
            started_at = lambda df: pd.to_datetime(df["started_at"]),
            day = lambda df: df["started_at"].dt.day,
            month = lambda df: df["started_at"].dt.month,
            year = lambda df: df["started_at"].dt.year,
            classic_bike = lambda df: df["rideable_type"].eq("classic_bike").map(int),
            electric_bike = lambda df: df["rideable_type"].eq("electric_bike").map(int),
            docked_bike = lambda df: df["rideable_type"].eq("docked_bike").map(int),
            member = lambda df: df["member_casual"].eq("member").map(int),
            casual = lambda df: df["member_casual"].eq("casual").map(int)
            )
        .drop(columns=["ride_id", "rideable_type", "started_at", "ended_at", "start_station_name",
                    "start_station_id", "end_station_name", "end_station_id", "member_casual"])
        .groupby(["month", "day", "year"]).sum()
        .assign(
            total_rides = lambda df: df["classic_bike"] + df["electric_bike"] + df["docked_bike"],
            # year = 2022,
            month = lambda df: df.index.get_level_values(0),
            day = lambda df: df.index.get_level_values(1),
            year = lambda df: df.index.get_level_values(2),
            date = lambda df: pd.to_datetime(df[["year", "month", "day"]]),
        )
        .reset_index(drop=True)
        # .set_index("date")
        .drop(columns=["year", "month", "day"])
    )

    return day_df


def create_ridership_dataframe(data_path="./data"):
    zip_paths = sorted(glob.glob(os.path.join(data_path, "*capitalbikeshare*.zip")))
    main_df = None
    for zip_path in zip_paths:
        df = aggregate_daily_ride_data(load_ride_data_zip(zip_path))
        if main_df is None:
            main_df = df.copy()
        else:
            main_df = pd.concat([main_df, df])
            main_df = main_df.reset_index(drop=True)
    return main_df


def read_weather_data(file_path):
    df = pd.read_csv(file_path, parse_dates=["DATE"])
    attr_cols = [x for x in df.columns if "_ATTRIBUTES" in x]
    wt_na_dict = {x: 0 for x in df.columns if "WT" in x}

    df = (
        df.copy()
        # we are only interested in data from 2018 and onward
        .loc[lambda df: df["DATE"] >= "2018-01-01"]
        .loc[lambda df: df["DATE"] <= "2022-05-31"]
        # drop attribute columns
        .drop(columns=attr_cols)
        # drop columns we do not need
        .drop(columns=["PGTM", "WDF1", "WDF2", "WDF5", "ACMH", "ACSH", "FMTM",
                    "FRGT", "WDFG", "WDFM", "WSF1", "WSFM",
                    "LATITUDE", "LONGITUDE", "ELEVATION", "NAME"])
        # dropping columns that are all NaN for our date range
        # these are features I would have used if they were not all NaN
        .drop(columns=["PSUN", "TSUN", "WESD", "WSFG", "WV20"])
        .fillna(value=wt_na_dict)

        # convert values to correct units for
        .assign(
            # convert precipitation from mm to m
            PRCP = lambda df: df["PRCP"].divide(1000),
            SNOW = lambda df: df["SNOW"].divide(1000),
            SNWD = lambda df: df["SNWD"].divide(1000),
            # convert temperature features from tenth of degree C to degree C
            TMAX = lambda df: df["TMAX"].divide(10),
            TMIN = lambda df: df["TMIN"].divide(10),
            TAVG = lambda df: df["TAVG"].divide(10)
        )  
    )

    return df


def create_weather_situation(df):
    wx_df = (
        df.copy()
        .assign(WXSIT = 0)
        .assign(WXSIT = lambda df: df["WXSIT"]
                    .add(df["WT13"])  # Mist
                    .add(df["WT01"])  # Fog
                    .add(df["PRCP"].gt(0).map(int))  # any rain
                    .clip(upper=1))
        .assign(WXSIT = lambda df: df["WXSIT"]
                    .add(2*df["WT02"])  # Heavy fog
                    .add(2*df["WT03"]) # thunder
                    .add(2*df["PRCP"].gt(0.15).map(int))  # greater than 0.15 m (~6 in) of rain
                    .add(2*df["SNOW"].gt(0).map(int))
                    .add(2*df["WT08"])  # Smoke or haze
                    .clip(upper=2))
        .assign(WXSIT = lambda df: df["WXSIT"]
                    .add(3*df["WT04"])  # Ice pellets, sleet, snow pellets, or small hail
                    .add(3*df["WT05"])  # Hail
                    .add(3*df["WT09"])  # Blowing or drifting snow
                    .add(3*df["PRCP"].gt(0.3).map(int))  # greater than 0.3 m (~12 in) of rain
                    .clip(upper=3))
        .drop(columns=[x for x in df.columns if "WT" in x])
    )

    return wx_df


def process_weather_data(file_path):
    df = read_weather_data(file_path)
    return create_weather_situation(df)
