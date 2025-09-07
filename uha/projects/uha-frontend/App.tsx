// App.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import MainScreen from './screens/MainScreen';

export default function App() {
    return (
        <View style={styles.container}>
            <MainScreen />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
});
