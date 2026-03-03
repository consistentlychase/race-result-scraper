import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json
import os
import config
import requests



RACES = config.RACES


def get_weather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?"


    with open(f"data/race_meta_data.json", 'r') as f:
        race_data = json.load(f)


    for i in range(len(RACES)): # DO THIS 5 TIMES

        for key, value in race_data[i].items(): # LOOKS AT ONE RACE AT A TIME ex: i = [0] = santa cruz
            race_name = key
            each_race_index = race_data[i][race_name]

            os.makedirs(f'data/weather/{race_name}', exist_ok=True)
            if os.path.exists(f'data/weather.csv'):
                pass
            else:

                # ----------------- GET COORDINATES FOR CURRENT RACE  ----------------- #
                for key, value in RACES.items(): 
                    for _ in range(len(RACES)): 
                        data_name = key

                    if race_name == data_name:
                        city = RACES[key]['city']
                        state = RACES[key]['state']
                        country = RACES[key]['country']

                        params = {
                            "name": city,
                            "count": "10",
                            "language": "en",
                            "countryCode": country
                        }
                        

                        response = requests.get(geo_url, params=params)
                        weather_data = response.json()
                        
                        for l in weather_data['results']:
                            data_state = l['admin1']
                            if data_state == state:
                                latitude = weather_data['results'][0]['latitude']
                                longitude = weather_data['results'][0]['longitude']
                                timezone = weather_data['results'][0]['timezone'] 

                                for j in range(len(each_race_index)): # LOOKS AT ONE YEAR AT A TIME
                                    current_race_date = race_data[i][race_name][j]['race_date']
                                    current_race_year = race_data[i][race_name][j]['year']

                                    parameters = {
                                        "latitude": latitude,
                                        "longitude": longitude,
                                        "start_date": current_race_date,
                                        "end_date": current_race_date,
                                        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain", "cloud_cover"],
                                        "timezone": timezone,
                                    }

                                    responses = openmeteo.weather_api(weather_url, params=parameters)

                                    # Process first location. Add a for-loop for multiple locations or weather models
                                    response = responses[0]


                                    # Process hourly data. The order of variables needs to be the same as requested.
                                    hourly = response.Hourly()
                                    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
                                    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
                                    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
                                    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
                                    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()

                                    hourly_data = {"date": pd.date_range(
                                        start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
                                        end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
                                        freq = pd.Timedelta(seconds = hourly.Interval()),
                                        inclusive = "left"
                                    )}

                                    hourly_data["temperature_2m"] = hourly_temperature_2m
                                    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
                                    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
                                    hourly_data["rain"] = hourly_rain
                                    hourly_data["cloud_cover"] = hourly_cloud_cover


                                    hourly_dataframe = pd.DataFrame(data = hourly_data)
                                    hour_range_df = hourly_dataframe.iloc[6:16].reset_index(drop=True)
                                    hour_range_df['date'] = hour_range_df['date'].dt.hour

                                    # Rename Columns
                                    hour_range_df.rename(columns={'date': 'time', 'temperature_2m': 'temperature', 'relative_humidity_2m': 'relative_humidity', 'wind_speed_10m':'wind_speed'}, inplace=True)
                                    
                                    # Create CSV of DB
                                    hour_range_df.to_csv(f'data/weather/{race_name}/{race_name}_weather_{current_race_year}.csv', index=False)


                                break # if state matches, stop and don't continue loop

                        break # If race name matches, then stop and dont conitnue the loop
