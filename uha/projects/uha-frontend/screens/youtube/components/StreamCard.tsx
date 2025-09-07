import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Linking, Animated } from 'react-native';

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

interface StreamCardProps {
    stream: StreamData;
}

export default function StreamCard({ stream }: StreamCardProps) {
    const scaleAnim = new Animated.Value(1);

    const formatNumber = (num?: number): string => {
        if (!num) return '0';
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return num.toString();
    };

    const handlePressIn = () => {
        Animated.spring(scaleAnim, {
            toValue: 0.98,
            useNativeDriver: true,
        }).start();
    };

    const handlePressOut = () => {
        Animated.spring(scaleAnim, {
            toValue: 1,
            useNativeDriver: true,
        }).start();
    };

    const formatDate = (dateStr: string): string => {
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('ko-KR', {
                month: 'short',
                day: 'numeric',
                weekday: 'short'
            });
        } catch {
            return dateStr;
        }
    };

    const formatDuration = (duration?: string): string => {
        if (!duration) return '';
        // ISO 8601 duration format (PT1H2M3S) to readable format
        const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
        if (!match) return duration;
        
        const hours = match[1] ? parseInt(match[1]) : 0;
        const minutes = match[2] ? parseInt(match[2]) : 0;
        const seconds = match[3] ? parseInt(match[3]) : 0;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const handlePress = () => {
        Linking.openURL(stream.url);
    };

    return (
        <Animated.View style={[styles.cardContainer, { transform: [{ scale: scaleAnim }] }]}>
            <TouchableOpacity 
                style={styles.card} 
                onPress={handlePress}
                onPressIn={handlePressIn}
                onPressOut={handlePressOut}
                activeOpacity={1}
            >
            {/* Thumbnail */}
            <View style={styles.thumbnailContainer}>
                {stream.thumbnail ? (
                    <Image 
                        source={{ uri: stream.thumbnail }} 
                        style={styles.thumbnail}
                        resizeMode="cover"
                    />
                ) : (
                    <View style={styles.placeholderThumbnail}>
                        <Text style={styles.placeholderText}>📺</Text>
                    </View>
                )}
                
                {/* Duration overlay */}
                {stream.duration && (
                    <View style={styles.durationOverlay}>
                        <Text style={styles.durationText}>
                            {formatDuration(stream.duration)}
                        </Text>
                    </View>
                )}
            </View>

            {/* Content */}
            <View style={styles.content}>
                {/* Date and Category */}
                <View style={styles.headerRow}>
                    <Text style={styles.dateText}>
                        {formatDate(stream.date)}
                    </Text>
                    {stream.category && (
                        <View style={styles.categoryBadge}>
                            <Text style={styles.categoryText}>{stream.category}</Text>
                        </View>
                    )}
                </View>

                {/* Title */}
                <Text style={styles.title} numberOfLines={2}>
                    {stream.title || 'Live Stream'}
                </Text>

                {/* AI Summary */}
                {stream.ai_summary && (
                    <View style={styles.summaryContainer}>
                        <Text style={styles.summaryText} numberOfLines={3}>
                            {stream.ai_summary}
                        </Text>
                    </View>
                )}

                {/* Stats */}
                <View style={styles.statsContainer}>
                    {stream.view_count !== undefined && (
                        <View style={styles.statItem}>
                            <Text style={styles.statIcon}>👁</Text>
                            <Text style={styles.statText}>
                                {formatNumber(stream.view_count)}
                            </Text>
                        </View>
                    )}
                    {stream.like_count !== undefined && (
                        <View style={styles.statItem}>
                            <Text style={styles.statIcon}>👍</Text>
                            <Text style={styles.statText}>
                                {formatNumber(stream.like_count)}
                            </Text>
                        </View>
                    )}
                    {stream.comment_count !== undefined && (
                        <View style={styles.statItem}>
                            <Text style={styles.statIcon}>💬</Text>
                            <Text style={styles.statText}>
                                {formatNumber(stream.comment_count)}
                            </Text>
                        </View>
                    )}
                    {/* Engagement Score */}
                    {stream.engagement_score !== undefined && stream.engagement_score > 0 && (
                        <View style={styles.statItem}>
                            <Text style={styles.statIcon}>⚡</Text>
                            <Text style={styles.statText}>
                                {stream.engagement_score}
                            </Text>
                        </View>
                    )}
                </View>

                {/* Sentiment */}
                {stream.sentiment && (
                    <View style={styles.sentimentContainer}>
                        <Text style={styles.sentimentText}>
                            {stream.sentiment}
                        </Text>
                    </View>
                )}

                {/* Highlights */}
                {stream.highlights && stream.highlights.length > 0 && (
                    <View style={styles.highlightsContainer}>
                        <Text style={styles.highlightsTitle}>💡 하이라이트</Text>
                        <View style={styles.highlightsList}>
                            {stream.highlights.slice(0, 2).map((highlight, index) => (
                                <View key={index} style={styles.highlightItem}>
                                    <Text style={styles.highlightText}>{highlight}</Text>
                                </View>
                            ))}
                        </View>
                    </View>
                )}

                {/* Keywords */}
                {stream.keywords && stream.keywords.length > 0 && (
                    <View style={styles.keywordsContainer}>
                        {stream.keywords.slice(0, 3).map((keyword, index) => (
                            <View key={index} style={styles.keywordTag}>
                                <Text style={styles.keywordText}>{keyword}</Text>
                            </View>
                        ))}
                    </View>
                )}

                {/* Tags */}
                {stream.tags && stream.tags.length > 0 && (
                    <View style={styles.tagsContainer}>
                        {stream.tags.slice(0, 2).map((tag, index) => (
                            <View key={index} style={styles.tag}>
                                <Text style={styles.tagText}>#{tag}</Text>
                            </View>
                        ))}
                    </View>
                )}
            </View>
            </TouchableOpacity>
        </Animated.View>
    );
}

const styles = StyleSheet.create({
    cardContainer: {
        marginHorizontal: 20,
        marginBottom: 16,
    },
    card: {
        backgroundColor: '#FFFFFF',
        borderRadius: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 4,
        },
        shadowOpacity: 0.08,
        shadowRadius: 12,
        elevation: 6,
        overflow: 'hidden',
        borderWidth: 0.5,
        borderColor: '#F3F4F6',
    },
    thumbnailContainer: {
        position: 'relative',
        height: 200,
        backgroundColor: '#F9FAFB',
    },
    thumbnail: {
        width: '100%',
        height: '100%',
    },
    placeholderThumbnail: {
        width: '100%',
        height: '100%',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F3F4F6',
    },
    placeholderText: {
        fontSize: 32,
    },
    durationOverlay: {
        position: 'absolute',
        bottom: 12,
        right: 12,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        borderRadius: 8,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    durationText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: '600',
    },
    content: {
        padding: 20,
    },
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    dateText: {
        fontSize: 13,
        color: '#4F46E5',
        fontWeight: '700',
        letterSpacing: 0.5,
    },
    categoryBadge: {
        backgroundColor: '#EEF2FF',
        borderRadius: 16,
        paddingHorizontal: 12,
        paddingVertical: 4,
    },
    categoryText: {
        fontSize: 11,
        color: '#4F46E5',
        fontWeight: '600',
    },
    title: {
        fontSize: 18,
        fontWeight: '700',
        color: '#111827',
        marginBottom: 12,
        lineHeight: 24,
        letterSpacing: -0.2,
    },
    summaryContainer: {
        backgroundColor: '#F8FAFC',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        borderLeftWidth: 4,
        borderLeftColor: '#4F46E5',
    },
    summaryText: {
        fontSize: 14,
        color: '#475569',
        lineHeight: 20,
        fontWeight: '500',
    },
    statsContainer: {
        flexDirection: 'row',
        marginBottom: 16,
        flexWrap: 'wrap',
        paddingTop: 8,
        borderTopWidth: 1,
        borderTopColor: '#F1F5F9',
    },
    statItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 16,
        marginBottom: 8,
        backgroundColor: '#F8FAFC',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 8,
    },
    statIcon: {
        fontSize: 14,
        marginRight: 4,
    },
    statText: {
        fontSize: 13,
        color: '#6c757d',
        fontWeight: '500',
    },
    keywordsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 8,
    },
    keywordTag: {
        backgroundColor: '#e3f2fd',
        borderRadius: 12,
        paddingHorizontal: 8,
        paddingVertical: 4,
        marginRight: 6,
        marginBottom: 4,
    },
    keywordText: {
        fontSize: 11,
        color: '#1976d2',
        fontWeight: '500',
    },
    tagsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    tag: {
        backgroundColor: '#f8f9fa',
        borderRadius: 8,
        paddingHorizontal: 6,
        paddingVertical: 2,
        marginRight: 4,
        marginBottom: 4,
        borderWidth: 1,
        borderColor: '#e9ecef',
    },
    tagText: {
        fontSize: 10,
        color: '#6c757d',
        fontWeight: '500',
    },
    // 새로 추가된 스타일들
    sentimentContainer: {
        backgroundColor: '#e8f5e8',
        borderRadius: 6,
        paddingHorizontal: 8,
        paddingVertical: 4,
        marginBottom: 8,
        alignSelf: 'flex-start',
    },
    sentimentText: {
        fontSize: 11,
        color: '#28a745',
        fontWeight: '500',
    },
    highlightsContainer: {
        marginBottom: 12,
    },
    highlightsTitle: {
        fontSize: 12,
        fontWeight: '600',
        color: '#333',
        marginBottom: 6,
    },
    highlightsList: {
        flexDirection: 'column',
    },
    highlightItem: {
        backgroundColor: '#fff3cd',
        borderRadius: 4,
        paddingHorizontal: 8,
        paddingVertical: 4,
        marginBottom: 4,
        borderLeftWidth: 2,
        borderLeftColor: '#ffc107',
    },
    highlightText: {
        fontSize: 11,
        color: '#856404',
        fontWeight: '500',
    },
});
