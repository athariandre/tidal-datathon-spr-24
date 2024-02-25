import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image } from 'react-native';

export function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Image source={{uri: 'https://cdn.pixabay.com/animation/2023/03/31/04/15/04-15-05-521_512.gif'}} style={styles.gifStyle} resizeMode="contain" />
        <Text style={styles.headerText}>routr.</Text>
        <TouchableOpacity
          style={styles.fancyButton}
          onPress={() => navigation.navigate('StartPosition')}
        >
          <Text style={styles.buttonText}>get started</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.copyrightText}>© 2024 routr. All rights reserved.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'transparent', 
    alignItems: 'center',
    justifyContent: 'space-between', // Adjusted for spacing between content and copyright
    flex: 1,
    padding: 20, // Add padding for overall container
  },
  content: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1, // Takes up all available space, pushing the copyright to the bottom
    marginTop: 20, // Optional: Adjust if your content is too close to the status bar
  },
  gifStyle: {
    width: 200, 
    height: 200,
    marginBottom: 20, 
  },
  headerText: {
    fontSize: 60,
    color: 'black',
    marginBottom: 20,
    fontWeight: 'bold',
    fontFamily: 'ArchivoBlack-Regular'
  },
  fancyButton: {
    backgroundColor: 'black', 
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    borderWidth: 0.7,
    borderColor: 'black',
    elevation: 5,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'ArchivoBlack-Regular'
  },
  copyrightText: {
    fontSize: 14,
    color: 'gray',
    marginBottom: 10, 
  },
});
