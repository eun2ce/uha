import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, ActivityIndicator, Image } from 'react-native';

interface NaverProfile {
    nickname: string;
    member_level: string;
    visit_count: string;
    activity_score: string;
}

interface NaverArticle {
    title: string;
    date: string;
    view_count: string;
    comment_count: string;
    link: string;
}

export default function NaverCafeScreen() {
    const [profile, setProfile] = useState<NaverProfile | null>(null);
    const [articles, setArticles] = useState<NaverArticle[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [loadingMore, setLoadingMore] = useState(false);

    const fetchProfile = async () => {
        try {
            // Fetch Naver Cafe profile
            
            const response = await fetch("http://127.0.0.1:8000/naver-cafe/profile/");
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Profile data received
            setProfile(data);

        } catch (error) {
            console.error("Error fetching profile:", error);
            Alert.alert(
                "프로필 로딩 실패",
                error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다."
            );
        }
    };

    const fetchArticles = async (page: number = 1, append: boolean = false) => {
        if (append) {
            setLoadingMore(true);
        }

        try {
            // Fetch Naver Cafe posts
            
            const response = await fetch(`http://127.0.0.1:8000/naver-cafe/articles/1/${page}/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Post data received

            if (append) {
                setArticles(prev => [...prev, ...data.articles]);
            } else {
                setArticles(data.articles);
            }

        } catch (error) {
            console.error("Error fetching articles:", error);
            Alert.alert(
                "게시글 로딩 실패",
                error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다."
            );
        } finally {
            setLoadingMore(false);
        }
    };

    const loadMoreArticles = () => {
        if (!loadingMore) {
            const nextPage = currentPage + 1;
            setCurrentPage(nextPage);
            fetchArticles(nextPage, true);
        }
    };

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([
                fetchProfile(),
                fetchArticles(1, false)
            ]);
            setLoading(false);
        };

        loadData();
    }, []);

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#00C73C" />
                <Text style={styles.loadingText}>네이버 카페 데이터를 불러오는 중...</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>네이버 카페</Text>
                <Text style={styles.headerSubtitle}>활동 정보 및 게시글</Text>
            </View>

            {/* Profile Section */}
            {profile && (
                <View style={styles.profileSection}>
                    <View style={styles.profileHeader}>
                        <View style={styles.profileIcon}>
                            <Text style={styles.profileIconText}>👤</Text>
                        </View>
                        <View style={styles.profileInfo}>
                            <Text style={styles.profileNickname}>{profile.nickname}</Text>
                            <Text style={styles.profileLevel}>{profile.member_level}</Text>
                        </View>
                    </View>
                    
                    <View style={styles.profileStats}>
                        <View style={styles.statItem}>
                            <Text style={styles.statValue}>{profile.visit_count}</Text>
                            <Text style={styles.statLabel}>방문 수</Text>
                        </View>
                        <View style={styles.statDivider} />
                        <View style={styles.statItem}>
                            <Text style={styles.statValue}>{profile.activity_score}</Text>
                            <Text style={styles.statLabel}>활동 점수</Text>
                        </View>
                    </View>
                </View>
            )}

            {/* Articles Section */}
            <View style={styles.articlesSection}>
                <Text style={styles.sectionTitle}>최근 게시글</Text>
                
                {articles.map((article, index) => (
                    <View key={index} style={styles.articleCard}>
                        <Text style={styles.articleTitle} numberOfLines={2}>
                            {article.title}
                        </Text>
                        
                        <View style={styles.articleMeta}>
                            <Text style={styles.articleDate}>{article.date}</Text>
                            <View style={styles.articleStats}>
                                <View style={styles.articleStat}>
                                    <Text style={styles.articleStatIcon}>👁</Text>
                                    <Text style={styles.articleStatText}>{article.view_count}</Text>
                                </View>
                                <View style={styles.articleStat}>
                                    <Text style={styles.articleStatIcon}>💬</Text>
                                    <Text style={styles.articleStatText}>{article.comment_count}</Text>
                                </View>
                            </View>
                        </View>
                    </View>
                ))}

                {/* Load More Button */}
                <TouchableOpacity 
                    style={styles.loadMoreButton} 
                    onPress={loadMoreArticles}
                    disabled={loadingMore}
                >
                    {loadingMore ? (
                        <ActivityIndicator size="small" color="#00C73C" />
                    ) : (
                        <Text style={styles.loadMoreText}>더 보기</Text>
                    )}
                </TouchableOpacity>
            </View>
        </ScrollView>
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
    header: {
        backgroundColor: '#00C73C',
        paddingHorizontal: 16,
        paddingVertical: 20,
        paddingTop: 40,
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: '700',
        color: '#fff',
        marginBottom: 4,
    },
    headerSubtitle: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    profileSection: {
        backgroundColor: '#fff',
        margin: 16,
        borderRadius: 12,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    profileHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    profileIcon: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: '#00C73C',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 12,
    },
    profileIconText: {
        fontSize: 20,
        color: '#fff',
    },
    profileInfo: {
        flex: 1,
    },
    profileNickname: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 2,
    },
    profileLevel: {
        fontSize: 14,
        color: '#00C73C',
        fontWeight: '500',
    },
    profileStats: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: 16,
        borderTopWidth: 1,
        borderTopColor: '#e9ecef',
    },
    statItem: {
        flex: 1,
        alignItems: 'center',
    },
    statValue: {
        fontSize: 20,
        fontWeight: '700',
        color: '#333',
        marginBottom: 4,
    },
    statLabel: {
        fontSize: 12,
        color: '#6c757d',
    },
    statDivider: {
        width: 1,
        height: 40,
        backgroundColor: '#e9ecef',
        marginHorizontal: 16,
    },
    articlesSection: {
        margin: 16,
        marginTop: 0,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
    },
    articleCard: {
        backgroundColor: '#fff',
        borderRadius: 8,
        padding: 16,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 1,
        },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    articleTitle: {
        fontSize: 16,
        fontWeight: '500',
        color: '#333',
        marginBottom: 12,
        lineHeight: 22,
    },
    articleMeta: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    articleDate: {
        fontSize: 12,
        color: '#6c757d',
    },
    articleStats: {
        flexDirection: 'row',
    },
    articleStat: {
        flexDirection: 'row',
        alignItems: 'center',
        marginLeft: 12,
    },
    articleStatIcon: {
        fontSize: 12,
        marginRight: 4,
    },
    articleStatText: {
        fontSize: 12,
        color: '#6c757d',
    },
    loadMoreButton: {
        backgroundColor: '#fff',
        borderRadius: 8,
        paddingVertical: 12,
        alignItems: 'center',
        marginTop: 8,
        borderWidth: 1,
        borderColor: '#00C73C',
    },
    loadMoreText: {
        fontSize: 14,
        color: '#00C73C',
        fontWeight: '500',
    },
});
