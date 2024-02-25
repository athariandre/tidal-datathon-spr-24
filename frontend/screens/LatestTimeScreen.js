import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, Animated } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

export function LatestTime({ navigation, route }) {
  const { startCity, startPos, startId, endCity, endPos, endId } = route.params;
  const [date, setDate] = useState(new Date());
  const [time, setTime] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  // Separate Animated.Values for each button
  const fadeAnimDate = useRef(new Animated.Value(1)).current;
  const fadeAnimTime = useRef(new Animated.Value(1)).current;

  const onDateChange = (event, selectedDate) => {
    const currentDate = selectedDate || date;
    setDate(currentDate);
    setShowDatePicker(Platform.OS === 'ios');
  };

  const onTimeChange = (event, selectedTime) => {
    const currentTime = selectedTime || time;
    setTime(currentTime);
    setShowTimePicker(Platform.OS === 'ios');
  };

  const combineDateTime = () => {
    let dateTime = new Date(date);
    dateTime.setHours(time.getHours(), time.getMinutes());
    return dateTime;
  };

  const showDatePickerHandler = () => {
    setShowDatePicker(true);
    Animated.timing(fadeAnimDate, {
      toValue: 0,
      duration: 500,
      useNativeDriver: true,
    }).start();
  };

  const showTimePickerHandler = () => {
    setShowTimePicker(true);
    Animated.timing(fadeAnimTime, {
      toValue: 0,
      duration: 500,
      useNativeDriver: true,
    }).start();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Select your arrival time:</Text>
      <Animated.View style={{ ...styles.button, opacity: fadeAnimDate }}>
        <TouchableOpacity style={styles.button} onPress={showDatePickerHandler}>
          <Text style={styles.buttonText}>Select Date</Text>
        </TouchableOpacity>
      </Animated.View>
      {showDatePicker && (
        <DateTimePicker
          value={date}
          mode="date"
          display="default"
          onChange={onDateChange}
        />
      )}
      <Animated.View style={{ ...styles.button, opacity: fadeAnimTime }}>
        <TouchableOpacity style={styles.button} onPress={showTimePickerHandler}>
          <Text style={styles.buttonText}>Select Time</Text>
        </TouchableOpacity>
      </Animated.View>
      {showTimePicker && (
        <DateTimePicker
          value={time}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={onTimeChange}
        />
      )}
      <Text style={styles.dateTimeText}>Selected: {combineDateTime().toLocaleString()}</Text>
      <View style={styles.buttonGroup}>
        <TouchableOpacity style={[styles.button, styles.backButton]} onPress={() => navigation.goBack()}>
          <Text style={styles.buttonText}>Return</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.nextButton]} onPress={() => {
            navigation.navigate("MapScreen", { startCity, startPos, startId, endCity, endPos, endId, date: combineDateTime() });
          }}>
          <Text style={styles.buttonText}>Next</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'space-around', // This will provide more space between elements
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff', // Clean white background
  },
  label: {
    fontSize: 20,
    color: '#333', // Soft black for text
  },
  button: {
    backgroundColor: '#007bff', // A calm blue for buttons
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 30,
    elevation: 3, // Slight shadow for depth
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
  },
  dateTimeText: {
    fontSize: 18,
    color: '#555', // Grey for less emphasis
  },
  buttonGroup: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  backButton: {
    backgroundColor: '#6c757d', // Bootstrap secondary gray
  },
  nextButton: {
    backgroundColor: '#28a745', // Green for progression action
  },
});
