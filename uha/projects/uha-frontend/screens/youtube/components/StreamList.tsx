import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, ActivityIndicator, RefreshControl, Animated } from 'react-native';
import StreamCard from './StreamCard';
import Pagination from './Pagination';

interface StreamData {
    date: string;
    url: string;
    video_id: string;
    title?: string;
    thumbnail?: string;
    view_count?: number;
    like_count?: number;
    comment_count?: number;
    duration?: string;
    tags?: string[];
    keywords?: string[];
    // 새로 추가된 필드들
    ai_summary?: string;
    highlights?: string[];
    sentiment?: string;
    engagement_score?: number;
    category?: string;
}

interface StreamListResponse {
    streams: StreamData[];
    total_streams: number;
    current_page: number;
    total_pages: number;
    per_page: number;
}

interface StreamListProps {
    currentYear: number;
}

export default function StreamList({ currentYear }: StreamListProps) {
    const [streams, setStreams] = useState<StreamData[]>([]);
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalStreams, setTotalStreams] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const fetchStreams = async (page: number = 1, isRefresh: boolean = false) => {
        if (isRefresh) {
            setRefreshing(true);
        } else {
            setLoading(true);
        }
        setError(null);

        try {
            // Fetch stream list

            const response = await fetch("http://127.0.0.1:8000/llm/streams", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    year: currentYear,
                    page: page,
                    per_page: 12,
                    include_details: true
                })
            });

            // API response status

            if (!response.ok) {
                const errorData = await response.json();
                console.error("API error data:", errorData);
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data: StreamListResponse = await response.json();
            // Stream data received

            setStreams(data.streams);
            setCurrentPage(data.current_page);
            setTotalPages(data.total_pages);
            setTotalStreams(data.total_streams);

        } catch (error) {
            console.error("Error fetching streams:", error);
            const errorMessage = error instanceof Error ? error.message : "Unknown error occurred.";
            setError(errorMessage);
            Alert.alert(
                "Failed to Load Stream List",
                errorMessage
            );
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        fetchStreams(page);
        // Scroll to top on page change
        scrollViewRef.current?.scrollTo({ y: 0, animated: true });
    };

    const handleRefresh = () => {
        fetchStreams(currentPage, true);
    };

    // Reset to first page when year changes
    useEffect(() => {
        setCurrentPage(1);
        fetchStreams(1);
    }, [currentYear]);

    const scrollViewRef = React.useRef<ScrollView>(null);

    if (loading && streams.length === 0) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#007bff" />
                <Text style={styles.loadingText}>스트림 목록을 불러오는 중...</Text>
            </View>
        );
    }

    if (error && streams.length === 0) {
        return (
            <View style={styles.errorContainer}>
                <Text style={styles.errorText}>😔</Text>
                <Text style={styles.errorMessage}>{error}</Text>
            </View>
        );
    }

    if (streams.length === 0) {
        return (
            <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>📺</Text>
                <Text style={styles.emptyMessage}>
                    {currentYear}년 스트림 데이터가 없습니다.
                </Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>
                    {currentYear}년 라이브 스트림
                </Text>
                <Text style={styles.headerSubtitle}>
                    총 {totalStreams}개 스트림
                </Text>
            </View>

            {/* Stream Cards */}
            <ScrollView 
                ref={scrollViewRef}
                style={styles.scrollView}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={handleRefresh}
                        colors={['#007bff']}
                        tintColor="#007bff"
                    />
                }
            >
                <View style={styles.streamGrid}>
                    {streams.map((stream, index) => (
                        <View key={`${stream.video_id}-${index}`} style={styles.streamItem}>
                            <StreamCard stream={stream} />
                        </View>
                    ))}
                </View>

                {/* Loading indicator for page changes */}
                {loading && streams.length > 0 && (
                    <View style={styles.pageLoadingContainer}>
                        <ActivityIndicator size="small" color="#007bff" />
                        <Text style={styles.pageLoadingText}>로딩 중...</Text>
                    </View>
                )}
            </ScrollView>

            {/* Pagination */}
            <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: '#6c757d',
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
        paddingHorizontal: 32,
    },
    errorText: {
        fontSize: 48,
        marginBottom: 16,
    },
    errorMessage: {
        fontSize: 16,
        color: '#dc3545',
        textAlign: 'center',
        lineHeight: 24,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
    },
    emptyText: {
        fontSize: 48,
        marginBottom: 16,
    },
    emptyMessage: {
        fontSize: 16,
        color: '#6c757d',
        textAlign: 'center',
    },
    header: {
        backgroundColor: '#fff',
        paddingHorizontal: 16,
        paddingVertical: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: '700',
        color: '#333',
        marginBottom: 4,
    },
    headerSubtitle: {
        fontSize: 14,
        color: '#6c757d',
    },
    scrollView: {
        flex: 1,
    },
    streamGrid: {
        padding: 16,
    },
    streamItem: {
        marginBottom: 0, // StreamCard has its own marginBottom
    },
    pageLoadingContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: 20,
    },
    pageLoadingText: {
        marginLeft: 8,
        fontSize: 14,
        color: '#6c757d',
    },
});
