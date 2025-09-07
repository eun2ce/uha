import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Linking } from 'react-native';

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
    const formatNumber = (num?: number): string => {
        if (!num) return '0';
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return num.toString();
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
        <TouchableOpacity style={styles.card} onPress={handlePress}>
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
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        borderRadius: 12,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
        overflow: 'hidden',
    },
    thumbnailContainer: {
        position: 'relative',
        height: 180,
        backgroundColor: '#f0f0f0',
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
        backgroundColor: '#e9ecef',
    },
    placeholderText: {
        fontSize: 32,
    },
    durationOverlay: {
        position: 'absolute',
        bottom: 8,
        right: 8,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderRadius: 4,
        paddingHorizontal: 6,
        paddingVertical: 2,
    },
    durationText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: '600',
    },
    content: {
        padding: 16,
    },
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    dateText: {
        fontSize: 12,
        color: '#007bff',
        fontWeight: '600',
        textTransform: 'uppercase',
    },
    categoryBadge: {
        backgroundColor: '#e9ecef',
        borderRadius: 12,
        paddingHorizontal: 8,
        paddingVertical: 2,
    },
    categoryText: {
        fontSize: 10,
        color: '#495057',
        fontWeight: '500',
    },
    title: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
        lineHeight: 22,
    },
    summaryContainer: {
        backgroundColor: '#f8f9fa',
        borderRadius: 6,
        padding: 10,
        marginBottom: 12,
        borderLeftWidth: 3,
        borderLeftColor: '#007bff',
    },
    summaryText: {
        fontSize: 13,
        color: '#495057',
        lineHeight: 18,
        fontStyle: 'italic',
    },
    statsContainer: {
        flexDirection: 'row',
        marginBottom: 12,
        flexWrap: 'wrap',
    },
    statItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 12,
        marginBottom: 4,
    },
    statIcon: {
        fontSize: 14,
        marginRight: 4,
    },
    statText: {
        fontSize: 12,
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
