import React from 'react';
import { Image, View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface ContentProps {
    cafe: any;
    articles: any[];
    onArticlePress: (link: string) => void;
    onPageChange: (direction: string) => void;
    pageId: number;
}

const Content: React.FC<ContentProps> = ({ cafe, articles, onArticlePress, onPageChange, pageId }) => {
    return (
        <View style={styles.cardContainer}>
            {/* Naver Cafe Info */}
            <Image
                source={{ uri: cafe?.thumbnail || "https://via.placeholder.com/120" }}
                style={styles.thumbnail}
            />
            <Text style={styles.cafeName}>{cafe?.name || "알 수 없음"}</Text>
            <Text style={styles.members}>회원 수: {cafe?.members ? cafe.members.toLocaleString() : "정보 없음"}</Text>

            {/* Naver Cafe Articles */}
            <View style={styles.articlesContainer}>
                <Text style={styles.articlesTitle}>게시글 목록</Text>
                {articles.length > 0 ? (
                    articles.map((article, index) => (
                        <View key={index} style={styles.article}>
                            <TouchableOpacity onPress={() => onArticlePress(article.link)}>
                                <View style={styles.articleRow}>
                                    <Text style={styles.articleTitle}>{article.title}</Text>
                                    <Text style={styles.articleMeta}>
                                        {article.author} | {article.date}
                                    </Text>
                                </View>
                            </TouchableOpacity>
                        </View>
                    ))
                ) : (
                    <Text>게시글이 없습니다.</Text>
                )}

                {/* 페이지 네비게이션 버튼 */}
                <View style={styles.paginationContainer}>
                    <TouchableOpacity
                        onPress={() => onPageChange('previous')}
                        disabled={pageId <= 1}
                        style={[styles.paginationButton, pageId <= 1 && styles.disabledButton]}>
                        <Text style={styles.paginationButtonText}>이전</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        onPress={() => onPageChange('next')}
                        style={styles.paginationButton}>
                        <Text style={styles.paginationButtonText}>다음</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    cardContainer: {
        alignItems: 'center',
        padding: 20,
        backgroundColor: '#fff',
        borderRadius: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        marginBottom: 20,
    },
    thumbnail: {
        width: 120,
        height: 120,
        borderRadius: 60,
        marginBottom: 10,
    },
    cafeName: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 5,
    },
    members: {
        fontSize: 16,
        color: 'gray',
        marginBottom: 15,
    },
    articlesContainer: {
        width: '100%',
    },
    articlesTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    article: {
        marginBottom: 10,
    },
    articleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    articleTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        flex: 1,
    },
    articleMeta: {
        fontSize: 12,
        color: 'gray',
    },
    paginationContainer: {
        flexDirection: 'row',
        marginTop: 20,
    },
    paginationButton: {
        backgroundColor: '#007bff',
        padding: 10,
        borderRadius: 5,
        marginRight: 10,
    },
    paginationButtonText: {
        color: '#fff',
        fontSize: 14,
    },
    disabledButton: {
        backgroundColor: '#b0b0b0',
    },
});

export default Content;
