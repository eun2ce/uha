import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, StatusBar, Animated, ScrollView } from 'react-native';
import StreamList from './youtube/components/StreamList';
import SummarySection from './youtube/components/SummarySection';
import NaverCafeScreen from './naver/NaverCafeScreen';

type TabType = 'streams' | 'summary' | 'naver';

export default function MainScreen() {
    const [activeTab, setActiveTab] = useState<TabType>('streams');
    const [currentYear, setCurrentYear] = useState(2025);
    const [fadeAnim] = useState(new Animated.Value(1));
    const [slideAnim] = useState(new Animated.Value(0));

    const tabs = [
        { id: 'streams', title: '라이브 스트림', icon: '📺', color: '#4F46E5', gradient: ['#4F46E5', '#7C3AED'] },
        { id: 'summary', title: 'AI 요약', icon: '🤖', color: '#059669', gradient: ['#059669', '#0D9488'] },
        { id: 'naver', title: '네이버 카페', icon: '🟢', color: '#00C73C', gradient: ['#00C73C', '#00B33C'] },
    ];

    useEffect(() => {
        // 탭 변경 시 부드러운 애니메이션
        Animated.parallel([
            Animated.timing(fadeAnim, {
                toValue: 0,
                duration: 150,
                useNativeDriver: true,
            }),
            Animated.timing(slideAnim, {
                toValue: -20,
                duration: 150,
                useNativeDriver: true,
            }),
        ]).start(() => {
            Animated.parallel([
                Animated.timing(fadeAnim, {
                    toValue: 1,
                    duration: 200,
                    useNativeDriver: true,
                }),
                Animated.timing(slideAnim, {
                    toValue: 0,
                    duration: 200,
                    useNativeDriver: true,
                }),
            ]).start();
        });
    }, [activeTab]);

    const renderContent = () => {
        switch (activeTab) {
            case 'streams':
                return <StreamList currentYear={currentYear} />;
            case 'summary':
                return (
                    <SummarySection 
                        currentYear={currentYear} 
                        onYearChange={setCurrentYear} 
                    />
                );
            case 'naver':
                return <NaverCafeScreen />;
            default:
                return <StreamList currentYear={currentYear} />;
        }
    };

    const getCurrentTab = () => tabs.find(tab => tab.id === activeTab);

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="dark-content" backgroundColor="#fff" />
            
            {/* Modern Header */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <View>
                        <Text style={styles.headerTitle}>UHA</Text>
                        <Text style={styles.headerSubtitle}>스마트 콘텐츠 분석</Text>
                    </View>
                    <View style={[styles.headerBadge, { backgroundColor: getCurrentTab()?.color + '20' }]}>
                        <Text style={[styles.headerBadgeText, { color: getCurrentTab()?.color }]}>
                            {getCurrentTab()?.icon}
                        </Text>
                    </View>
                </View>
            </View>

            {/* Modern Tab Navigation */}
            <View style={styles.tabContainer}>
                <ScrollView 
                    horizontal 
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.tabScrollContent}
                >
                    {tabs.map((tab, index) => (
                        <TouchableOpacity
                            key={tab.id}
                            style={[
                                styles.tab,
                                activeTab === tab.id && [styles.activeTab, { backgroundColor: tab.color + '10' }]
                            ]}
                            onPress={() => setActiveTab(tab.id as TabType)}
                        >
                            <View style={[
                                styles.tabIconContainer,
                                activeTab === tab.id && { backgroundColor: tab.color }
                            ]}>
                                <Text style={[
                                    styles.tabIcon,
                                    activeTab === tab.id && styles.activeTabIcon
                                ]}>
                                    {tab.icon}
                                </Text>
                            </View>
                            <Text style={[
                                styles.tabText,
                                activeTab === tab.id && [styles.activeTabText, { color: tab.color }]
                            ]}>
                                {tab.title}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {/* Year Selector (only for streams and summary tabs) */}
            {(activeTab === 'streams' || activeTab === 'summary') && (
                <View style={styles.yearSelector}>
                    <ScrollView 
                        horizontal 
                        showsHorizontalScrollIndicator={false}
                        contentContainerStyle={styles.yearScrollContent}
                    >
                        {[2020, 2021, 2022, 2023, 2024, 2025].map((year) => (
                            <TouchableOpacity
                                key={year}
                                style={[
                                    styles.yearButton,
                                    currentYear === year && [
                                        styles.yearButtonActive,
                                        { backgroundColor: getCurrentTab()?.color }
                                    ]
                                ]}
                                onPress={() => setCurrentYear(year)}
                            >
                                <Text style={[
                                    styles.yearButtonText,
                                    currentYear === year && styles.yearButtonTextActive
                                ]}>
                                    {year}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                </View>
            )}

            {/* Content with Animation */}
            <Animated.View 
                style={[
                    styles.content,
                    {
                        opacity: fadeAnim,
                        transform: [{ translateY: slideAnim }]
                    }
                ]}
            >
                {renderContent()}
            </Animated.View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#FAFAFA',
    },
    header: {
        backgroundColor: '#FFFFFF',
        paddingHorizontal: 20,
        paddingTop: 16,
        paddingBottom: 20,
        borderBottomWidth: 0.5,
        borderBottomColor: '#E5E7EB',
    },
    headerContent: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    headerTitle: {
        fontSize: 28,
        fontWeight: '800',
        color: '#111827',
        letterSpacing: -0.5,
    },
    headerSubtitle: {
        fontSize: 15,
        color: '#6B7280',
        fontWeight: '500',
        marginTop: 2,
    },
    headerBadge: {
        width: 48,
        height: 48,
        borderRadius: 24,
        justifyContent: 'center',
        alignItems: 'center',
    },
    headerBadgeText: {
        fontSize: 20,
    },
    tabContainer: {
        backgroundColor: '#FFFFFF',
        paddingTop: 16,
        borderBottomWidth: 0.5,
        borderBottomColor: '#E5E7EB',
    },
    tabScrollContent: {
        paddingHorizontal: 20,
        paddingBottom: 16,
    },
    tab: {
        flexDirection: 'column',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 12,
        marginRight: 12,
        borderRadius: 16,
        backgroundColor: '#F9FAFB',
        minWidth: 100,
    },
    activeTab: {
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
    },
    tabIconContainer: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: '#E5E7EB',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 6,
    },
    tabIcon: {
        fontSize: 16,
    },
    activeTabIcon: {
        fontSize: 16,
    },
    tabText: {
        fontSize: 12,
        fontWeight: '600',
        color: '#6B7280',
        textAlign: 'center',
    },
    activeTabText: {
        fontWeight: '700',
    },
    yearSelector: {
        backgroundColor: '#FFFFFF',
        paddingVertical: 16,
        borderBottomWidth: 0.5,
        borderBottomColor: '#E5E7EB',
    },
    yearScrollContent: {
        paddingHorizontal: 20,
    },
    yearButton: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        marginRight: 12,
        borderRadius: 20,
        backgroundColor: '#F3F4F6',
        borderWidth: 1,
        borderColor: '#E5E7EB',
    },
    yearButtonActive: {
        borderColor: 'transparent',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    yearButtonText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#6B7280',
    },
    yearButtonTextActive: {
        color: '#FFFFFF',
        fontWeight: '700',
    },
    content: {
        flex: 1,
        backgroundColor: '#FAFAFA',
    },
});
