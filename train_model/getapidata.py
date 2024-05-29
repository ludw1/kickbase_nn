import requests
from time import sleep
import pandas as pd
from darts import TimeSeries

# path to save the data
csv_path = r""

# URL of the API endpoint
url = "https://api.kickbase.com/user/login"

# JSON payload for the request
# user needs to add email and password
payload = {
    "email": "",
    "password": "",
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
    league_id = response.json()["leagues"][1]["id"]
    user_id = response.json()["user"]["id"]
else:
    print("Error:", response.status_code)

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Cookie": f"kkstrauth={token};"
}
# this is the worst way to do this
knownIds = [4, 8, 36, 44, 46, 49, 51, 54, 60, 78, 89, 96, 97, 118, 163, 168, 173, 237, 262, 285, 304, 336, 357, 383, 387, 392, 399, 429, 450, 461, 477, 493, 496, 497, 513, 523, 524, 547, 550, 554, 573, 577, 579, 581, 608, 619, 620, 623, 651, 655, 660, 663, 668, 670, 699, 734, 737, 755, 841, 849, 1070, 1138, 1158, 1183, 1192, 1207, 1217, 1222, 1223, 1225, 1226, 1229, 1246, 1249, 1253, 1257, 1259, 1266, 1298, 1308, 1330, 1333, 1387, 1405, 1407, 1464, 1514, 1527, 1540, 1544, 1553, 1561, 1571, 1574, 1580, 1581, 1584, 1590, 1622, 1639, 1645, 1653, 1664, 1671, 1685, 1686, 1687, 1689, 1703, 1704, 1725, 1726, 1739, 1758, 1761, 1774, 1782, 1785, 1804, 1809, 1811, 1815, 1829, 1856, 1862, 1865, 1871, 1873, 1883, 1893, 1896, 1900, 1903, 1910, 1918, 1920, 1929, 1954, 1961, 1971, 1975, 1990, 1991, 2005, 2030, 2037, 2038, 2047, 2065, 2068, 2069, 2074, 2076, 2079, 2084, 2091, 2092, 2120, 2125, 2134, 2141, 2144, 2148, 2157, 2172, 2176, 2195, 2197, 2199, 2201, 2214, 2229, 2232, 2237, 2255, 2261, 2263, 2273, 2274, 2275, 2278, 2279, 2287, 2288, 2300, 2302, 2309, 2321, 2335, 2343, 2349, 2358, 2365, 2366, 2373, 2378, 2383, 2393, 2395, 2399, 2400, 2426, 2429, 2430, 2439, 2450, 2453, 2455, 2460, 2463, 2476, 2489, 2491, 2494, 2496, 2515, 2521, 2522, 2526, 2532, 2533, 2536, 2539, 2546, 2551, 2552, 2553, 2561, 2566, 2572, 2582, 2584, 2596, 2630, 2639, 2643, 2644, 2646, 2649, 2651, 2655, 2662, 2664, 2665, 2681, 2690, 2692, 2694, 2702, 2714, 2717, 2718, 2722, 2724, 2725, 2727, 2732, 2736, 2737, 2746, 2749, 2764, 2765, 2766, 2776, 2783, 2791, 2792, 2793, 2795, 2799, 2804, 2809, 2814, 2822, 2832, 2835, 2850, 2852, 2854, 2863, 2864, 2866, 2876, 2878, 2883, 2885, 2887, 2891, 2893, 2897, 2903, 2915, 2918, 2927, 2939, 2941, 2944, 2946, 2948, 2972, 2974, 2976, 2977, 2979, 2987, 2988, 2990, 2994, 3001, 3004, 3011, 3012, 3013, 3017, 3019, 3022, 3025, 3027, 3029, 3041, 3050, 3063, 3068, 3069, 3070, 3079, 3084, 3085, 3087, 3089, 3090, 3105, 3108, 3118, 3120, 3124, 3125, 3128, 3129, 3130, 3132, 3140, 3143, 3151, 3160, 3166, 3167, 3187, 3190, 3191, 3193, 3196, 3204, 3208, 3214, 3219, 3230, 3232, 3233, 3236, 3238, 3242, 3245, 3249, 3250, 3253, 3282, 3289, 3306, 3329, 3339, 3344, 3345, 3362, 3369, 3397, 3454, 3457, 3459, 3470, 3471, 3473, 3475, 3476, 3477, 3479, 3482, 3483, 3500, 3509, 3510, 3511, 3515, 3548]

for num,id in enumerate(knownIds):
    print("Percentage done:", num/len(knownIds)*100,"%")
    url = f"https://api.kickbase.com/leagues/{league_id}/players/{id}/feed" # for injury history
    url2 = f"https://api.kickbase.com/leagues/{league_id}/players/{id}/stats" # for marketvalue
    url3 = f"https://api.kickbase.com/leagues/{league_id}/players/{id}/" # for player name

    response = requests.get(url, headers=headers)
    sleep(0.2)
    response2 = requests.get(url2, headers=headers)
    sleep(0.2)
    response3 = requests.get(url3, headers=headers)
    if response.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
        injury_data = response.json()
        value_data = response2.json()
        name_data = response3.json()
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
        name_df = pd.DataFrame({"Name": [name_data["firstName"] + " " + name_data["lastName"]]*len(final_df)})
        final_df = pd.concat([name_df,final_df],axis=1)
        final_df = final_df.ffill()
        # this is so 1 = fit 0 = not fit
        final_df = final_df.fillna(1)
        final_df.to_csv(csv_path, mode='a', header=False, index=False, encoding="UTF-8")
    else:
        print("Error:", response.status_code)
    sleep(0.5)
