import React, {useState, useEffect} from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator, TransitionPresets, CardStyleInterpolators, TransitionSpecs} from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TouchableHighlight, Button, Touchable} from 'react-native';
import { EndPosScreen } from './screens/EndingPositionScreen';
import { StartPosScreen } from './screens/StartingPositionScreen';
import { HomeScreen } from './screens/HomeScreen';
import {LatestTime} from './screens/LatestTimeScreen';
import {MapScreen} from './screens/MapScreen';
import {AppLoading} from 'expo';
import * as Font from 'expo-font';

const Stack = createStackNavigator();

const loadFonts = () => Font.loadAsync ({

    'ArchivoBlack-Regular': require('./assets/ArchivoBlack-Regular.ttf'),

});

const forFade = ({ current, next }) => ({
  cardStyle: {
    opacity: current.progress,
  },
});

const config = {
  animation: 'spring',
  config: {
    stiffness: 1000,
    damping: 500,
    mass: 3,
    overshootClamping: true,
    restDisplacementThreshold: 0.01,
    restSpeedThreshold: 0.01,
  },
};



const horizontalAnimation = {
  cardStyleInterpolator: CardStyleInterpolators.forHorizontalIOS,
};

export default function App() {
  const [fontsLoaded, setFontsLoaded] = useState(false);

  useEffect(() => {
    loadFonts().then(() => setFontsLoaded(true));
  }, []);

  if(fontsLoaded){
    return ( 
      <NavigationContainer>
        <MyStack/>
      </NavigationContainer>
    );
  } else {
    <AppLoading
      startAsync={loadFonts}
      onFinish={()=> setFontsLoaded(true)}
    />
  }
  

}


function MyStack() {
  return (
    <Stack.Navigator screenOptions={{...horizontalAnimation}}>
      <Stack.Screen name="HomeScreen" component={HomeScreen} options={{
        headerShown: false, transitionSpec: {open: CardStyleInterpolators.forModalPresentationIOS, close: CardStyleInterpolators.forModalPresentationIOS}
      }}/>
      <Stack.Screen name="StartPosition" component={StartPosScreen} options={{
        headerShown: false, transitionSpec: {open: CardStyleInterpolators.forModalPresentationIOS, close: CardStyleInterpolators.forModalPresentationIOS}
      }}/>
      <Stack.Screen name="EndPosition" component={EndPosScreen} options={{
        headerShown: false, transitionSpec: {open: CardStyleInterpolators.forModalPresentationIOS, close: CardStyleInterpolators.forModalPresentationIOS}
      }}/>
      <Stack.Screen name="LatestTime" component={LatestTime} options={{
        headerShown: false, transitionSpec: {open: CardStyleInterpolators.forModalPresentationIOS, close: CardStyleInterpolators.forModalPresentationIOS}
      }}/>
      <Stack.Screen name="MapScreen" component={MapScreen} options={{
        headerShown: false, transitionSpec: {open: CardStyleInterpolators.forModalPresentationIOS, close: CardStyleInterpolators.forModalPresentationIOS}
      }}/>
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  testColor: {
    fontSize: 50,
    color: 'red',


  },
});
