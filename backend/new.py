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


class Path:


    origin = Point(0,0)
    destination = Point(0,0)
    weather = pd.dataFrame(columns=["date", "clear", "soil", "fog", "rain", "wind", "sleet", "snow"])
    score = 0


    def __init__(self, origin, destination, time): #starttime should be: #MM-DD-YYYY HH" #"%m-%d-%Y %H"
        self.origin = origin
        self.destination = destination
        self.time = datetime.strptime(time, "%m-%d-%Y %H")
    
    def getIndexedCoordinates(start_point, end_point):

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
    

    

    
    












def safestTime(origin, destination, starttime, endtime): #start and end time in format: "MM-DD-YYYY HH" (hr in 24-hr time)
    formatstring = "%m-%d-%Y %H"
    starttime_object = datetime.strptime(starttime, formatstring)
    endtime_object = datetime.strptime(endtime, formatstring)
    
    path_list = generatePaths(origin, destination, starttime_object, endtime_object)

    
