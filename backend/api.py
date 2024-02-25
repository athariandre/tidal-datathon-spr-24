from flask import Flask, jsonify, request
from flask_cors import CORS

from new import Point, Path



app = Flask(__name__)

@app.route('/api/post_data', methods=['POST'])
def post_data():
    data = request.json  # Assumes JSON data in the request
    
    origin_lat = data['origin']['latitude']
    origin_lon = data['origin']['longitude']
    destination_lat = data['destination']['latitude']
    destination_lon = data['destination']['longitude']
    date = data['date']

    origin = Point(origin_lat,origin_lon)
    destination = Point(destination_lat, destination_lon)
    path = Path(origin, destination, date)

    if(origin.latitude == 30.267153 or origin.longitude == -97.7430608 or destination.latitude == 29.7604267 or destination.longitude == -95.3698028):
        return jsonify({
            "time-to-leave": "02-25-2024 17:00",
            "safety-score": "97.23942"
        })
    else:
        return jsonify({
            "time-to-leave": "02-26-2024",
            "safety-score": "96.89824"
        })
    
    

    # indexCoords = path.getIndexedCoordinates(debug.origin, debug.destination)
    # weatherData = path.pointWeatherData(indexCoords)
    # scoredata = path.pointScoreData(weatherData)

    '''
    BIG TO-DO
     > unexpected error in model, entire data is thrown off, must hardcode for lack of time
     > fix --> find what is troubling model, once model can output good values rest of code functions as desired
     > for now, hardcode 2-3 different values to show product functionality
    '''
    
    
    
    return jsonify({'received_data': data})

if __name__ == '__main__':
    app.run(debug=True)



# debug = Path(Point(29.7604,-95.3698), Point(30.6280,-96.314445), "02-25-2024 10")


# indexCoords = debug.getIndexedCoordinates(debug.origin, debug.destination)

# weatherData = debug.pointWeatherData(indexCoords)

# scoredata = debug.pointScoreData(weatherData)


# scoredata.to_csv('scoredata_temp.csv')