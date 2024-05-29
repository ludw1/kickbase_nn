import pandas as pd
from darts import TimeSeries
from datetime import datetime
from dateutil.relativedelta import relativedelta
from darts.dataprocessing.transformers import Scaler

def clean_df(
        df : pd.DataFrame):
    """
    Clean the dataframe
    :param df: pd.DataFrame: Dataframe to clean
    :return: pd.DataFrame: Cleaned df"""

    # convert date time to date only
    df["Time"] = pd.to_datetime(df["Time"],format=("%d.%m.%Y %H:%M:%S")).dt.strftime('%d-%m-%y')
    # convert price to float
    df["Price"] = [float(i.replace("€","").replace(",",".").replace(".",""))/1e06 for i in df["Price"]]
    # divide points by 100
    df["Points"] = [float(i)/100 for i in df["Points"]]
    # convert fit, pos, Ver using one hot encoding
    df = pd.get_dummies(df, columns=["Ver"])
    df = pd.get_dummies(df, columns=["Pos"])
    df = pd.get_dummies(df, columns=["Fit"])
    return df

def dataloader(filepath : str, api : bool, in_len : int, out_len : int) -> list:
    """
    Load data from csv file
    :param filepath: str: Path to csv file
    :param api: bool: True if using api data
    :param in_len: int: Input length
    :param out_len: int: Output length
    :return: list: List of TimeSeries
    """
    if api:
        csv_head = ["Name", "Time", "Fit", "Price"]
    else: 
        csv_head = ["Name", "Ver", "Pos", "Points", "Price", "Fit", "Time"]
    df = pd.read_csv(filepath, encoding="UTF-8", names = csv_head, header = None)
    trainval_split = 0.7
    if api:
        df["Price"] = [float(i)/1e06 for i in df["Price"]]
        df["Time"] = pd.to_datetime(df["Time"],format=("%Y-%m-%d")).dt.strftime('%d-%m-%y')
        
    else:
        clean_df(df)
    df["Time"] = pd.to_datetime(df["Time"],format=("%d-%m-%y"))
    unique_players = df["Name"].unique()
    player_series_dict = {}
    fit_dict = {}
    for i in unique_players:
        player_df = df.query('Name == @i')
        # only consider players with at least 16 data points
        if len(player_df) < in_len + out_len:
            continue
        else:
            player_series_dict[i] = TimeSeries.from_dataframe(player_df, "Time", "Price", freq="D")
            if api:
                # drop data that go back more than one year
                fit_dict[i] = TimeSeries.from_dataframe(player_df, "Time","Fit", freq="D")
                player_series_dict[i] = player_series_dict[i].drop_before(pd.to_datetime(datetime.now() - relativedelta(years=1)))
                fit_dict[i] = fit_dict[i].drop_before(pd.to_datetime(datetime.now() - relativedelta(years=1)))
            else:
                fit_dict[i] = TimeSeries.from_dataframe(player_df, "Time","Fit_Fit", freq="D")
    time_series_list = list(player_series_dict.values())
    fit_list = list(fit_dict.values())
    scaler = Scaler()
    train = []
    val = []
    past_cov_t = []
    past_cov_v = []
    for series,fit in zip(time_series_list,fit_list):
        traintemp, valtemp = (scaler.fit_transform(series).split_after(trainval_split))
        past_cov_train_temp, past_cov_val_temp = (scaler.fit_transform(fit).split_after(trainval_split))
        # check if series is long enough
        if len(valtemp) > in_len + out_len:
            train.append(traintemp)
            val.append(valtemp)
            past_cov_t.append(past_cov_train_temp)
            past_cov_v.append(past_cov_val_temp)
    return train, val, past_cov_t, past_cov_v, time_series_list 