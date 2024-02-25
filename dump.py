import json
import openmeteo_requests
import pandas as pd
import requests_cache
import requests

from datetime import datetime
from retry_requests import retry

def lambda_handler(event, context):
    
    event_json = json.loads(event['body'])

    start_city = event_json['start-city']
    end_city = event_json['end-city']
    
    url = "https://api.open-meteo.com/v1/forecast"
    
    url_locs = "https://fc237dvgydqwc7utwn472f3e5m0qifll.lambda-url.us-east-2.on.aws/"
    
    params_loc = {
        "start-city": start_city,
        "end-city": end_city
    }
    
    response = requests.post(url_locs, json = params_loc)
    response_json = response.json()
    
    duration = response.json()['duration']
    datapoints = json.loads(response.json()['datapoints'])
    
    latstr = ""
    lonstr = ""
    
    for datapoint in datapoints:
      lat = datapoint[0]
      lon = datapoint[1]
      latstr+=str(lat)+","
      lonstr+=str(lon)+","
    latstr = latstr[:-1]
    lonstr = lonstr[:-1]
    
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    params = {
    	"latitude": latstr,
    	"longitude": lonstr,
    	"hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "wind_speed_10m"],
      "temperature_unit": "fahrenheit",
      "timezone": "America/Chicago",
      "start_date": "2024-02-27",
      "end_date": "2024-02-27"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    
    df = pd.DataFrame(columns = ["Date", "relative_humidity_2m", "rain", "snowfall", "wind_speed_10m", "sleet", "clear" "latitude", "longitude"])
    
    for response in responses:
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
        hourly_rain = hourly.Variables(3).ValuesAsNumpy()
        hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
        hourly_rain = hourly.Variables(3).ValuesAsNumpy()
        hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["rain"] = hourly_rain
        hourly_data["snowfall"] = hourly_snowfall
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

        hourly_dataframe = pd.DataFrame(data = hourly_data)
      
        hourly_dataframe["sleet"] = 0

        #Define conditions for sleet
        sleet_conditions = (
            (hourly_dataframe['temperature_2m'] <= 32) &
            (hourly_dataframe['snowfall'] == 0) &
            (hourly_dataframe["precipitation"])> 0.0     
        )
        hourly_dataframe['sleet'] = 0.0                     
        hourly_dataframe.loc[sleet_conditions, 'sleet'] = 1.0  
        
        
        #turn everything into boolean 0 and 1
        for i,row in hourly_dataframe.iterrows():
            temp = row["relative_humidity_2m"]
            if temp > 83.0:
                hourly_dataframe.at[i,"relative_humidity_2m"] = 1.0
            else:
                hourly_dataframe.at[i,"relative_humidity_2m"] = 0.0
        
        
        for i,row in hourly_dataframe.iterrows():
            temp = row["rain"]
            if temp > 0.0:
                hourly_dataframe.at[i,"rain"] = 1.0
            else:
                hourly_dataframe.at[i,"rain"] = 0.0
        
        
        for i,row in hourly_dataframe.iterrows():
            temp = row["snowfall"]
            if temp > 0.0:
                hourly_dataframe.at[i,"snowfall"] = 1.0
            else:
                hourly_dataframe.at[i,"snowfall"] = 0.0
        
        for i,row in hourly_dataframe.iterrows():
            temp = row["wind_speed_10m"]
            if temp >= 10.0:
                hourly_dataframe.at[i,"wind_speed_10m"] = 1.0
            else:
                hourly_dataframe.at[i,"wind_speed_10m"] = 0.0
        
        #Define conditions for clear
        clear_conditions = (
            (hourly_dataframe['snowfall'] == 0.0) &
            (hourly_dataframe['rain'] == 0.0) &
            (hourly_dataframe["wind_speed_10m"] == 0.0) & 
            (hourly_dataframe["relative_humidity_2m"] == 0.0) &
            (hourly_dataframe["sleet"] == 0.0)
        )
        hourly_dataframe['clear'] = 0.0                     
        hourly_dataframe.loc[clear_conditions, 'clear'] = 1.0
        
        
        drop_columns = ['temperature_2m','precipitation','cloud_cover_high','soil_temperature_0cm']
        hourly_dataframe= hourly_dataframe.drop(columns=drop_columns)
        
        hourly_dataframe['Date'] = hourly_dataframe['date'].dt.strftime('%Y-%m-%d')
        hourly_dataframe['Time'] = hourly_dataframe['date'].dt.strftime('%H:%M')
        
        drop_columns = ['date']
        hourly_dataframe= hourly_dataframe.drop(columns=drop_columns)
        
        hourly_dataframe = hourly_dataframe[['Date', 'Time'] + [col for col in hourly_dataframe.columns if col not in ['Date', 'Time']]]
        
        hourly_dataframe['latitude'] = response.Latitude()
        hourly_dataframe['longitude'] = response.Longitude()
        
        df = pd.concat([df, hourly_dataframe], ignore_index=True)
    
    array_2d = [df.columns.tolist()] + df.values.tolist()
        
    return {
        "statusCode": 200,
        "body": json.dumps(array_2d)
    }   
    