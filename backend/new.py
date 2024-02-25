import json
import requests
import polyline
import joblib
import openmeteo_requests
import pandas as pd
import requests_cache

from datetime import datetime
from retry_requests import retry


key = "AIzaSyAblqkZYB0S1noTtq-GWTImAFk0PYcvGvs"
loaded_model = joblib.load('backend/model_drt.joblib')


class Point:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class Path:

    origin = Point(0,0)
    destination = Point(0,0)
    weather = pd.DataFrame(columns=["date", "clear", "soil", "fog", "rain", "wind", "sleet", "snow"])
    score = 0


    def __init__(self, origin, destination, time): #starttime should be: #MM-DD-YYYY HH" #"%m-%d-%Y %H"
        self.origin = origin
        self.destination = destination
        self.time = datetime.strptime(time, "%m-%d-%Y %H")
    
    def getIndexedCoordinates(self, start_point, end_point):

        fields = "routes.polyline.encodedPolyline,routes.duration"
        routeurl = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={key}&fields={fields}"

        route_json = {
            "origin": {
                "via": False,
                "vehicleStopover": False,
                "sideOfRoad": False,
                "location": {
                    "latLng":{
                        "latitude": start_point.latitude,
                        "longitude": start_point.longitude
                    }
                }
            },
            "destination": {
                "via": False,
                "vehicleStopover": False,
                "sideOfRoad": False,
                "location": {
                    "latLng":{
                        "latitude": end_point.latitude,
                        "longitude": end_point.longitude
                    }
                }
            }
        }
        
        route_json_string = json.dumps(route_json)
        response = requests.post(routeurl, route_json_string)
        response_json = response.json()


        encoded_polyline = response_json['routes'][0]['polyline']['encodedPolyline']
        decoded_polyline = polyline.decode(encoded_polyline)
        decoded_polyline = decoded_polyline[::2]

        duration = float(response_json['routes'][0]['duration'][:-1])

        point_list = []
        for point in decoded_polyline:
            lat = point[0]
            lon = point[1]
            point_list.append(Point(lat,lon))

        return point_list
    
    def pointWeatherData(self, point_list):

        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        url = "https://api.open-meteo.com/v1/forecast"


        latstr = ""
        lonstr = ""
        
        for datapoint in point_list:
            lat = datapoint.latitude
            lon = datapoint.longitude
            latstr+=str(lat)+","
            lonstr+=str(lon)+","

        latstr = latstr[:-1]
        lonstr = lonstr[:-1]

        params = {
            "latitude": latstr,
            "longitude": lonstr,
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "cloud_cover_high", "wind_speed_10m", "soil_temperature_0cm"],
            "temperature_unit": "fahrenheit",
            "timezone": "America/Chicago",
            "start_date": "2024-02-27",
            "end_date": "2024-02-27"
        }


        responses = openmeteo.weather_api(url, params=params)

            
        for response in responses:
            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
            hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
            hourly_rain = hourly.Variables(3).ValuesAsNumpy()
            hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
            hourly_cloud_cover_high = hourly.Variables(5).ValuesAsNumpy()
            hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()
            hourly_soil_temperature_0cm = hourly.Variables(7).ValuesAsNumpy()

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
            hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
            hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
            hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm

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

            hourly_dataframe['date'] = hourly_dataframe['date'].astype(str)
                
            for i,row in hourly_dataframe.iterrows():
                temp = row["date"]
                temp = temp[:-12]
                hourly_dataframe.at[i,"date"] = temp
                
            hourly_dataframe['soil'] = 0.0


            hourly_dataframe = hourly_dataframe.rename(columns={'relative_humidity_2m': 'fog', 'wind_speed_10m': 'wind','snowfall': 'snow'})

            column_order = ['date', 'clear','soil', 'fog', 'rain', 'wind', 'sleet','snow']
            hourly_dataframe = hourly_dataframe[column_order]
            self.weather = pd.concat([self.weather, hourly_dataframe], axis=0)
        return self.weather
    
    def pointScoreData(self, weather_list):
        weather_list['score'] = 700  # Initialize score column with base value
        for index, item in weather_list.iterrows():
            score = item['score']  # Retrieve the current score value
            if int(item['clear']) == 1:
                score *= 0.75
            if int(item['soil']) == 1:
                score *= 2
            if int(item['fog']) == 1:
                score *= 1.23294812
            if int(item['rain']) == 1:
                score *= 3
            if int(item['wind']) == 1:
                score *= 1
            if int(item['sleet']) == 1:
                score *= 4
            if int(item['snow']) == 1:
                score *= 5
            # Update the 'score' column with the calculated value
            weather_list.at[index, 'score'] = score

        return weather_list

    
    

debug = Path(Point(29.7604,-95.3698), Point(30.6280,-96.314445), "02-25-2024 10")


indexCoords = debug.getIndexedCoordinates(debug.origin, debug.destination)

weatherData = debug.pointWeatherData(indexCoords)

scoredata = debug.pointScoreData(weatherData)


scoredata.to_csv('scoredata_temp.csv')

    
