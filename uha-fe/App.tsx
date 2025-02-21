import React from 'react';
import {DefaultTheme, NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Ionicons} from '@expo/vector-icons';
import YouTubeScreen from './screens/youtube/YouTubeScreen';
import CafeScreen from './screens/cafe/CafeScreen';

const Tab = createBottomTabNavigator();
const MyTheme = {
    ...DefaultTheme,
    colors: {
        ...DefaultTheme.colors,
        primary: 'rgb(255, 45, 85)',
    },
};

export default function App() {
    return (
        <NavigationContainer theme={MyTheme}>
            <Tab.Navigator
                initialRouteName="YouTube"
                screenOptions={({route}) => ({
                    tabBarIcon: ({color, size}) => {
                        let iconName: string;

                        if (route.name === 'YouTube') {
                            iconName = 'logo-youtube';
                        } else if (route.name === 'Cafe') {
                            iconName = 'cafe';
                        }

                        return <Ionicons name={iconName} size={size} color={color}/>;
                    },
                    tabBarActiveTintColor: '#FF6347',  // 활성화된 탭 아이콘 색상
                    tabBarInactiveTintColor: '#B0B0B0', // 비활성화된 탭 아이콘 색상
                    tabBarStyle: {
                        backgroundColor: '#ffffff', // 네비게이션 바 배경 색상
                        borderTopWidth: 0,  // 상단 테두리 제거
                        elevation: 5,  // 그림자 효과
                    },
                    tabBarLabelStyle: {
                        fontSize: 12,  // 레이블 텍스트 크기
                        fontWeight: 'bold',  // 레이블 텍스트 굵기
                    },
                    tabBarItemStyle: {
                        paddingVertical: 10, // 아이템 간 간격
                    },
                })}
            >
                <Tab.Screen name="YouTube" component={YouTubeScreen} options={{headerShown: false}}/>
                <Tab.Screen name="Cafe" component={CafeScreen} options={{headerShown: false}}/>
            </Tab.Navigator>
        </NavigationContainer>
    );
}
