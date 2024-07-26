import requests
from time import sleep
import pandas as pd
from darts import TimeSeries
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from nn_predict import nn_predict
from scipy.optimize import curve_fit
import tomllib
# import config
config_path = input("Please input path to config file: ")
with open(config_path, "rb") as f:
    config = tomllib.load(f)
print(config)

offered_players = {}

def clean_apidata(injury_data : dict, value_data : dict) -> tuple[TimeSeries, TimeSeries] | None:
    """
    Clean the api data so we have 2 clean timeseries
    :param injury_data: dict: Injury data from api
    :param value_data: dict: Market value data from api
    :return: TimeSeries: Cleaned timeseries or None"""
    fit_days= [] # list to store the days where the player was fit
    value_days = [] # list to store the days where the player had a market value
    values = [] # list to store the market values
    fit_data = [] # list to store the fit data
    for dict_1 in value_data['marketValues']:
        days = dict_1['d'].replace("T"," ").replace("Z","") # clean up datetime data
        price = dict_1['m']
        value_days.append(days)
        values.append(price)
    for item in (injury_data["items"]):
        if item["type"] == 14: # type 14 is injury
            if "meta" in item: # sometimes the meta data is missing
                fit_days.append(item["date"].replace("T"," ").replace("Z",""))
                fit_data.append("Fit" in item["meta"].get("s","Fit"))
    # this next part is very messy, but it works
    # convert the lists into dataframes and make sure the time is in the right format
    fit_df = pd.DataFrame({"Time": fit_days, "Fit": fit_data})
    wert_df = pd.DataFrame({"Time": value_days, "Wert": values})
    wert_df["Time"] = pd.to_datetime(wert_df["Time"],format=("%Y-%m-%d %H:%M:%S")).dt.strftime('%d-%m-%y')
    wert_df["Time"] = pd.to_datetime(wert_df["Time"],format=("%d-%m-%y"))
    fit_df["Time"] = pd.to_datetime(fit_df["Time"],format=("%Y-%m-%d %H:%M:%S")).dt.strftime('%d-%m-%y')
    fit_df["Time"] = pd.to_datetime(fit_df["Time"],format=("%d-%m-%y"))
    fit_df = fit_df.drop_duplicates(subset="Time")
    # this is needed to fill all days where there is no fit data
    # therefore we ffill
    tempseries = TimeSeries.from_dataframe(fit_df, "Time", "Fit",freq="D")
    tempfit_df = tempseries.pd_dataframe()
    tempfit_df = tempfit_df.sort_values(by="Time").ffill()
    tempfit_df["Time"] = pd.to_datetime(tempfit_df.index)
    tempseries = TimeSeries.from_dataframe(tempfit_df, "Time", "Fit",freq="D")
    tempfit_df = tempseries.pd_dataframe()
    tempfit_df = tempfit_df.reset_index()
    # merge fit data and marketvalues
    final_df = pd.merge(tempfit_df,wert_df, on="Time", how="right")
    final_df = final_df.ffill()
    # this is so 1 = fit 0 = not fit
    final_df = final_df.fillna(1)
    # now we turn the data into two seperate timeseries again
    if len(final_df) < 35:
        return None
    fit_series = TimeSeries.from_dataframe(final_df, "Time", "Fit", freq="D")
    value_series = TimeSeries.from_dataframe(final_df, "Time", "Wert", freq="D")
    # if the start time is more than a year, drop everything before
    if value_series.start_time() < pd.to_datetime(datetime.now() - relativedelta(years=1)):
        value_series = value_series.drop_before(pd.to_datetime(datetime.now() - relativedelta(years=1)))
    return value_series, fit_series

# ensure that user is logged in on first run
last_login = datetime.now() - timedelta(days=1, minutes=1)
last_market_check = datetime.now() - timedelta(hours=2)

# main loop
while True:
    curr_time = datetime.now()
    if curr_time - last_login > timedelta(days=1):
        # refresh login token once a day and collect gift
        url = "https://api.kickbase.com/user/login"

        # JSON payload for the request
        # user needs to add email and password
        payload = {
            "email": config["email"],
            "password": config["password"],
            "ext": False
        }

        # headers for the request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # sending the POST request
        response = requests.post(url, json=payload, headers=headers)

        # Extracting the token from the response JSON
        if response.status_code == 200:
            token = response.json()["token"]
            leagues = response.json()["leagues"]
            user_id = response.json()["user"]["id"]
        else:
            print("Error:", response.status_code)
        league_id = [league["id"] for league in leagues if league["name"] == "Alex Stinkt"][0]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"kkstrauth={token};"
        }
        # collect gift
        gift_url = f"https://api.kickbase.com/leagues/{league_id}/collectgift"
        gift_response = requests.post(gift_url, headers=headers)
        last_login = datetime.now()
    if curr_time - last_market_check > timedelta(hours=1):
        url = f"https://api.kickbase.com/leagues/{league_id}/market"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            market_data = response.json()
        # get current budget before making bids
        budget_url = f"https://api.kickbase.com/leagues/{league_id}/me"
        response = requests.get(budget_url, headers=headers)
        if response.status_code == 200:
            budget_data = response.json()
            budget = budget_data["budget"]
        # remove players that expired
        for player in offered_players:
            if offered_players[player] < datetime.now():
                del offered_players[player]

        for player in market_data["players"]:
            expiry = player["expiry"] # time to expire in seconds
            player_id = player["id"]
            if player_id in offered_players:
                continue
            player_filter = [(expiry < (60*60*config["low_time_bound"]) or expiry > (60*60*24*config["high_time_bound"])), 
                             (player["marketValue"] < config["marketvaluelimit"]), (player["marketValueTrend"] == 2) and config["onlyrisingplayer"]
                             , (player["status"] != 0 and config["onlyfitplayer"])]
            print(player_filter)
            print(player)
            if True in player_filter:
                continue
            
            url2 = f"https://api.kickbase.com/leagues/{league_id}/players/{player_id}/stats"
            url3 = f"https://api.kickbase.com/leagues/{league_id}/players/{player_id}/feed"
            mw_response = requests.get(url2, headers=headers)
            sleep(0.2)
            injury_response = requests.get(url3, headers=headers)
            if mw_response.status_code == 200 and injury_response.status_code == 200:
                injury_data = injury_response.json()
                value_data = mw_response.json()
                value_series, fit_series = clean_apidata(injury_data, value_data)
                if value_series is None:
                    continue
                # now pass to model
                pred = nn_predict(value_series, fit_series, config["modelpath"], config["lookahead"])
                # now fit a polynomial function to the prediction including the last value
                prediction_points = [value_series.pd_series().tolist()[-1]] + pred.pd_series().tolist()
                pred_fit = curve_fit(lambda x,a,b,c,d,e: a*x**4 + b*x**3 + c*x**2 + d*x + e, np.array(range(len(prediction_points))), prediction_points)
                pred_function = lambda x: pred_fit[0][0]*x**4 + pred_fit[0][1]*x**3 + pred_fit[0][2]*x**2 + pred_fit[0][3]*x + pred_fit[0][4]
                # scale offer by overpay value
                offer = pred_function(config["risk_value"]) * (1 + config["overpay"])
                if offer > budget:
                    continue
                else:
                    budget -= offer
                offer_url = f"https://api.kickbase.com/leagues/{league_id}/market/{player_id}/offers"
                offer_payload = {
                    "price": offer
                }
                playername = player["firstName"] + " " + player["lastName"]
                print(f"Offering {offer} for player {playername}")
                offer_response = requests.post(offer_url, json=offer_payload, headers=headers)
                offered_players[player_id] = datetime.now() + relativedelta(seconds=expiry) # store player id and time when expired
                last_market_check = datetime.now()
    # if the time is close to 10 pm, sleep till shortly after 10 pm
    if curr_time.hour == 22 or (curr_time.hour == 21 and curr_time.minute > 10):
        sleep(60*60)
    else:
        sleep(60*60*2)