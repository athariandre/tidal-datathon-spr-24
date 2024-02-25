import React, { useRef } from 'react';
import { View, Button, Dimensions, StyleSheet, Text, StatusBar, Alert, SafeAreaView, TouchableOpacity } from 'react-native';
import MapView, { PROVIDER_GOOGLE, Marker } from "react-native-maps";
import MapViewDirections from "react-native-maps-directions";

const { width, height } = Dimensions.get("window");
const aspectRatio = width / height;
const LatitudeDelta = 0.0922;
const LongitudeDelta = LatitudeDelta * aspectRatio;

const GOOGLE_MAPS_APIKEY = 'AIzaSyAblqkZYB0S1noTtq-GWTImAFk0PYcvGvs';
// const postData = async (url = '', data = {}) => {
//   const response = await fetch(url, {
//     method: 'POST', 
//     mode: 'cors', 
//     cache: 'no-cache',
//     credentials: 'same-origin', 
//     headers: {
//       'Content-Type': 'application/json'

//     },
//     redirect: 'follow',
//     referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
//     body: JSON.stringify(data) // body data type must match "Content-Type" header
//   });
//   return response.json(); // parses JSON response into native JavaScript objects
// }

// postData('https://example.com/your-api-endpoint', { answer: 42 })
//   .then(data => {
//     console.log(data); // JSON data parsed by `response.json()` call
//   });


export function MapScreen({ navigation, route }) {
  const { startCity, startPos, startId, endCity, endPos, endId, date } = route.params;
  const mapRef = useRef(null);


  // Convert the date to a readable string format
  const dateString = new Date(date).toLocaleDateString();

  return (
    <>
      <MapView
        ref={mapRef}
        style={StyleSheet.absoluteFillObject}
        provider={PROVIDER_GOOGLE}
        initialRegion={{
          latitude: startPos.lat,
          longitude: startPos.lng,
          latitudeDelta: LatitudeDelta,
          longitudeDelta: LongitudeDelta,
        }}
      >
        <Marker
          coordinate={{latitude: startPos.lat, longitude: startPos.lng}}
          title={startCity}
        >
          <View style={styles.customMarker}>
            <Text style={styles.markerText}>A</Text>
          </View>
        </Marker>
        <Marker
          coordinate={{latitude: endPos.lat, longitude: endPos.lng}}
          title={endCity}
        >
          <View style={styles.customMarker}>
            <Text style={styles.markerText}>B</Text>
          </View>
        </Marker>
        <MapViewDirections
          origin={`place_id:${startId}`}
          destination={`place_id:${endId}`}
          apikey={GOOGLE_MAPS_APIKEY}
          strokeWidth={4}
          strokeColor="darkblue"
          onReady={result => {
            mapRef.current.fitToCoordinates(result.coordinates, {
              edgePadding: {
                right: (width / 20),
                bottom: (height / 20),
                left: (width / 20),
                top: (height / 20),
              }
            });
          }}
          onError={(errorMessage) => {
            Alert.alert("Error", "Failed to retrieve directions. Please try again.");
          }}
        />
      </MapView>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="dark-content" backgroundColor="#ecf0f1" />
        <View style={styles.overlay}>
          <Text style={styles.bottomText}>Trip on {dateString}</Text>
          <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
            <Text style={styles.buttonText}>Return</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    position: 'absolute',
    bottom: 0, // Adjusted to only apply to the bottom to ensure overlay is at the bottom
    left: 0,
    right: 0,
  },
  overlay: {
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)', // Optional: Added background color for visibility
    paddingVertical: 20, // Added padding for spacing around the text and button
  },
  button: {
    backgroundColor: "#007bff",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    marginTop: 10, // Space between the text and the button
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  bottomText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff', // Changed text color for better visibility on dark background
    marginBottom: 10, // Space between the text and the button
  },
  customMarker: {
    backgroundColor: "darkblue",
    padding: 10,
    borderRadius: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  markerText: {
    color: "#fff",
    fontWeight: "bold",
  },
});
