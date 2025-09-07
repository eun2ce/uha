// App.tsx
import React from 'react';
import {ScrollView, StyleSheet, View} from 'react-native';
import YouTubeScreen from './screens/youtube/YouTubeScreen'; // YouTubeScreen 경로에 맞게 수정
import CafeScreen from './screens/cafe/CafeScreen'; // CafeScreen 경로에 맞게 수정
import Header from './screens/common/Header'; // Header 컴포넌트 임포트

export default function App() {
    return (
        <ScrollView style={styles.container}>
            {/* Header */}
            <Header />

            {/* Main Content */}
            <View style={styles.contentContainer}>
                {/* YouTube Screen */}
                <View style={styles.screenContainer}>
                    <YouTubeScreen />
                </View>

                {/* Cafe Screen */}
                <View style={styles.screenContainer}>
                    <CafeScreen />
                </View>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        // backgroundColor: '#f5f5f5', // 배경 색상 추가
    },
    contentContainer: {
        flex: 1, // 나머지 공간을 차지하도록 설정
        flexDirection: 'row', // 가로로 배치
        justifyContent: 'space-between', // 화면을 좌우로 배치
        alignItems: 'flex-start', // 세로로 상단 정렬
        padding: 10, // 내부 여백
    },
    screenContainer: {
        flex: 1, // 화면을 균등하게 나누기 위해
        padding: 10, // 내부 여백
        justifyContent: 'center', // 세로 중앙 정렬
    },
});
