import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView, ImageBackground } from 'react-native';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';

const fetchCityImage = async (city) => {
  const accessKey = 'Sdst52rj3sdpZTLZ24pMQKDv4j2XntBKVxIhBEDxa6I';
  // Adding 'cityscape' as an example to narrow down search results to city-related images
  const url = `https://api.unsplash.com/search/photos?page=1&query=${encodeURIComponent(city + ' cityscape')}&client_id=${accessKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    if (data.results.length > 0) {
      return data.results[0].urls.regular;
    }
  } catch (error) {
    console.error("Error fetching city image:", error);
  }
  return null;
};




export function StartPosScreen({ navigation }) {
  const [startCity, setStartCity] = useState('');
  const [startPos, setStartPos] = useState('');
  const [startId, setStartId] = useState('');
  const [bgImageUrl, setBgImageUrl] = useState('https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/White_square_50%25_transparency.svg/2048px-White_square_50%25_transparency.svg.png'); // Placeholder image URL

  return (
    <ImageBackground
      source={{ uri: bgImageUrl }}
      resizeMode="cover"
      style={styles.backgroundImage}
    >
      <SafeAreaView style={styles.container}>
        <Text style={styles.label}>Starting City:</Text>
        <View style={styles.autocompleteContainer}>
          <GooglePlacesAutocomplete
            fetchDetails={true}
            placeholder='Search'
            onPress={async (data, details = null) => {
              setStartCity(data.description);
              setStartId(data.place_id);
              setStartPos(details?.geometry?.location);
              const imageUrl = await fetchCityImage(data.description);
              setBgImageUrl(imageUrl); // Update the background image URL
            }}
            query={{
              key: 'AIzaSyAblqkZYB0S1noTtq-GWTImAFk0PYcvGvs', // Replace with your actual Google Places API key
              language: 'en',
            }}
            styles={{

              textInput: styles.textInput,
              listView: styles.listView,
              separator: styles.separator,
            }}
            onFail={error => console.error(error)}
          />
        </View>
        
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={[styles.button, styles.backButton]} onPress={() => navigation.goBack()}>
            <Text style={styles.buttonText}>Go Back</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, styles.nextButton, !startCity && styles.disabledButton]}
            onPress={() => navigation.navigate("EndPosition", {startCity, startPos, startId})}
            disabled={!startCity}
          >
            <Text style={styles.buttonText}>Next</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  label: {
    fontSize: 20,
    marginBottom: 15,
    fontWeight: 'bold',
    color: 'black', // Changed to white for better visibility on image background
  },
  autocompleteContainer: {
    width: '90%',
    height: '50%',
  },
  textInputContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)', // Slightly transparent for better visibility
    borderTopWidth: 0,
    borderBottomWidth: 0,
    borderRadius: 200000000,
  },
  textInput: {
    height: 50,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: '#cccccc',
    fontSize: 16,
    width: '100%',
  },
  listView: {
    borderWidth: 1,
    borderColor: '#cccccc',
    backgroundColor: 'rgba(255, 255, 255, 0.9)', // Slightly transparent
  },
  separator: {
    height: 1,
    backgroundColor: '#cccccc',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: 30,
  },
  button: {
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 20,
    alignItems: 'center',
  },
  backButton: {
    backgroundColor: '#6c757d',
  },
  nextButton: {
    backgroundColor: '#28a745',
  },
  disabledButton: {
    backgroundColor: '#cccccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
