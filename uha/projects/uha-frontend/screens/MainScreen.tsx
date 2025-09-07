import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, StatusBar } from 'react-native';
import StreamList from './youtube/components/StreamList';
import SummarySection from './youtube/components/SummarySection';
import NaverCafeScreen from './naver/NaverCafeScreen';

type TabType = 'streams' | 'summary' | 'naver';

export default function MainScreen() {
    const [activeTab, setActiveTab] = useState<TabType>('streams');
    const [currentYear, setCurrentYear] = useState(2025);

    const tabs = [
        { id: 'streams', title: '라이브 스트림', icon: '📺' },
        { id: 'summary', title: 'AI 요약', icon: '🤖' },
        { id: 'naver', title: '네이버 카페', icon: '🟢' },
    ];

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

    const getTabColor = (tabId: string) => {
        switch (tabId) {
            case 'streams':
                return '#007bff';
            case 'summary':
                return '#28a745';
            case 'naver':
                return '#00C73C';
            default:
                return '#6c757d';
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="dark-content" backgroundColor="#fff" />
            
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>UHA Dashboard</Text>
                <Text style={styles.headerSubtitle}>YouTube & 네이버 카페 분석</Text>
            </View>

            {/* Year Selector (only for streams and summary tabs) */}
            {(activeTab === 'streams' || activeTab === 'summary') && (
                <View style={styles.yearSelector}>
                    <Text style={styles.yearLabel}>연도:</Text>
                    <View style={styles.yearButtons}>
                        {[2020, 2021, 2022, 2023, 2024, 2025].map((year) => (
                            <TouchableOpacity
                                key={year}
                                style={[
                                    styles.yearButton,
                                    currentYear === year && styles.yearButtonActive
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
                    </View>
                </View>
            )}

            {/* Tab Navigation */}
            <View style={styles.tabContainer}>
                {tabs.map((tab) => (
                    <TouchableOpacity
                        key={tab.id}
                        style={[
                            styles.tab,
                            activeTab === tab.id && [
                                styles.activeTab,
                                { borderBottomColor: getTabColor(tab.id) }
                            ]
                        ]}
                        onPress={() => setActiveTab(tab.id as TabType)}
                    >
                        <Text style={styles.tabIcon}>{tab.icon}</Text>
                        <Text style={[
                            styles.tabText,
                            activeTab === tab.id && [
                                styles.activeTabText,
                                { color: getTabColor(tab.id) }
                            ]
                        ]}>
                            {tab.title}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            {/* Content */}
            <View style={styles.content}>
                {renderContent()}
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    header: {
        backgroundColor: '#fff',
        paddingHorizontal: 16,
        paddingVertical: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: '700',
        color: '#333',
        marginBottom: 4,
    },
    headerSubtitle: {
        fontSize: 14,
        color: '#6c757d',
    },
    yearSelector: {
        backgroundColor: '#fff',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
        flexDirection: 'row',
        alignItems: 'center',
    },
    yearLabel: {
        fontSize: 14,
        fontWeight: '500',
        color: '#333',
        marginRight: 12,
    },
    yearButtons: {
        flexDirection: 'row',
        flex: 1,
    },
    yearButton: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        marginRight: 8,
        borderRadius: 16,
        backgroundColor: '#f8f9fa',
        borderWidth: 1,
        borderColor: '#dee2e6',
    },
    yearButtonActive: {
        backgroundColor: '#007bff',
        borderColor: '#007bff',
    },
    yearButtonText: {
        fontSize: 12,
        fontWeight: '500',
        color: '#6c757d',
    },
    yearButtonTextActive: {
        color: '#fff',
    },
    tabContainer: {
        flexDirection: 'row',
        backgroundColor: '#fff',
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
    },
    tab: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 16,
        borderBottomWidth: 3,
        borderBottomColor: 'transparent',
    },
    activeTab: {
        borderBottomWidth: 3,
    },
    tabIcon: {
        fontSize: 16,
        marginRight: 6,
    },
    tabText: {
        fontSize: 14,
        fontWeight: '500',
        color: '#6c757d',
    },
    activeTabText: {
        fontWeight: '600',
    },
    content: {
        flex: 1,
    },
});
