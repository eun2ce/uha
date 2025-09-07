// App.tsx
import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import MainScreen from './screens/MainScreen';

const { width } = Dimensions.get('window');

export default function App() {
    return (
        <View style={styles.container}>
            <View style={styles.mobileContainer}>
                <MainScreen />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
        justifyContent: 'center',
        alignItems: 'center',
    },
    mobileContainer: {
        width: Math.min(width, 430), // 최대 430px (iPhone 14 Pro Max 크기)
        height: '100%',
        backgroundColor: '#ffffff',
        borderRadius: width > 430 ? 16 : 0,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 4,
        },
        shadowOpacity: 0.1,
        shadowRadius: 12,
        elevation: 8,
    },
});
