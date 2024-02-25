import json
import requests
import polyline
import lightgbm as lgb
import joblib
import openmeteo_requests
import pandas as pd
import requests_cache

from datetime import datetime, timedelta
from retry_requests import retry
from backend.weather_processing import *

key = "AIzaSyAblqkZYB0S1noTtq-GWTImAFk0PYcvGvs"


class Point:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class Trip:
    def __init__(self, start_point, end_point, earliest_time, latest_time):
        self.start_point = start_point
        self.end_point = end_point
    def getIndexedCoordinates(start_point, end_point):

        fields = "routes.polyline.encdodedPolyline,routes.duration"
        routeurl = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={key}&fields={fields}"

        route_json = {
            "origin": {
                "via": False,
                "vehicleStopover": False,
                "sideOfRoad": False,
                "address": origin
            },
            "destination": {
                "via": False,
                "vehicleStopover": False,
                "sideOfRoad": False,
                "address": destination
            }
        }
        
        route_json_string = json.dumps(route_json)
        response = requests.post(routeurl, route_json_string)
        response_json = response.json()

        encoded_polyline = response_json['routes'][0]['polyline']['encodedPolyline']
        decoded_polyline = polyline.decode(encoded_polyline)
        decoded_polyline = decoded_polyline[::2]

        point_list = []

        for point in decoded_polyline:
            lat = point[0]
            lon = point[1]
            point_list.append(Point(lat,lon))
        return point_list

    def getTripWeather(point_list):
        return tripWeatherCalculator(point_list)






    datapoints = 
    
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
event = {
    'start-city': "Houston, TX",
    'end-city': "College Station, TX",
    'start-time': "01-01-2024 01:01",
    'end-time': "01-05-2024 05:30"
}
    

origin = event['start-city']
destination = event['end-city']