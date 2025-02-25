import React, {memo, useEffect, useState} from 'react';
import {ActivityIndicator, FlatList, Image, Linking, StyleSheet, Text, TouchableOpacity, View} from 'react-native';
import {useAssets} from "expo-asset";

interface ContentProps {
    cafe: any;
    onArticlePress: (link: string) => void;
    pageId: number;
}

const Content: React.FC<ContentProps> = ({cafe, onArticlePress, pageId}) => {
    const [selectedTab, setSelectedTab] = useState<number>(0);
    const [tabArticles, setTabArticles] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [totalPages, setTotalPages] = useState<number>(50); // 예시로 50페이지로 설정
    const [assets] = useAssets([require("../../../assets/screens/cafe/cafe_default_thumbnail.png")]);

    const tabs = [
        {name: '공지사항', apiNumber: 1},
        {name: '자유게시판', apiNumber: 6},
        {name: '팬영상(쇼츠) 게시판', apiNumber: 16},
        {name: '웃음참기', apiNumber: 11},
    ];

    const fetchArticles = async (page: number) => {
        setLoading(true);
        const apiNumber = tabs[selectedTab]?.apiNumber;
        try {
            const response = await fetch(`http://127.0.0.1:8000/naver-cafe/articles/${apiNumber}/${page}/`);
            const data = await response.json();
            setHasMore(data.result.length > 0); // 더 많은 데이터가 있을 경우 true
            setTabArticles(data.result); // 새 데이터로 덮어쓰지 않고 기존 데이터를 추가함
            setTotalPages(data.totalPages || 10); // 전체 페이지 수 설정 (응답에 맞게 설정)
        } catch (error) {
            console.error("Error fetching articles:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setCurrentPage(1); // 탭 변경 시 페이지 초기화
        setTabArticles([]); // 탭 변경 시 게시글 초기화
        fetchArticles(1); // 첫 페이지 데이터 로드
    }, [selectedTab]);

    const handleTabChange = (index: number) => {
        setSelectedTab(index);
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setCurrentPage(newPage);
            fetchArticles(newPage);
        }
    };

    const renderItem = ({item}: { item: any }) => {
        const today = new Date();
        const isDateOnly = item.date.length === 10; // '2025.01.09' 형태
        const articleDate = isDateOnly
            ? new Date(`${today.getFullYear()}-${item.date.replace(/\./g, '-')}T00:00:00`)
            : new Date(`${today.toISOString().split('T')[0]}T${item.date}`);

        const isToday = today.toDateString() === articleDate.toDateString(); // 오늘 날짜와 비교

        const hasImage = item.image && item.image.length > 0;

        return (
            <View style={styles.article}>
                <TouchableOpacity onPress={() => onArticlePress(item.link)}>
                    <View style={styles.articleRow}>
                        <Text
                            style={styles.articleTitle}
                            numberOfLines={1}
                            ellipsizeMode="tail"
                        >
                            {item.title}
                            {hasImage && <Text style={styles.imageIcon}> 📷</Text>}
                            {isToday && <Text style={styles.newIcon}> 🆕</Text>}
                        </Text>
                        <Text style={styles.articleMeta}> {item.author} | {item.date}</Text>
                    </View>
                </TouchableOpacity>
            </View>
        );
    };

    const renderFooter = () => {
        if (!loading) return null;
        return <ActivityIndicator size="large" color="#007bff" style={styles.footerLoader}/>;
    };

    const renderPageButtons = () => {
        const startPage = Math.max(currentPage - 2, 1);
        const endPage = Math.min(startPage + 4, totalPages);

        const pages = [];
        if (startPage > 1) {
            pages.push(
                <TouchableOpacity
                    key="prev-ellipsis"
                    onPress={() => handlePageChange(startPage - 1)}
                    style={styles.pageButton}
                >
                    <Text style={styles.pageButtonText}>{"<"}</Text>
                </TouchableOpacity>
            );
        }

        for (let i = startPage; i <= endPage; i++) {
            pages.push(
                <TouchableOpacity
                    key={i}
                    onPress={() => handlePageChange(i)}
                    style={[
                        styles.pageButton,
                        currentPage === i && styles.selectedPageButton,
                    ]}
                >
                    <Text style={styles.pageButtonText}>{i}</Text>
                </TouchableOpacity>
            );
        }

        if (endPage < totalPages) {
            pages.push(
                <TouchableOpacity
                    key="next-ellipsis"
                    onPress={() => handlePageChange(endPage + 1)}
                    style={styles.pageButton}
                >
                    <Text style={styles.pageButtonText}>{">"}</Text>
                </TouchableOpacity>
            );
        }

        return pages;
    };

    return (
        <View style={styles.container}>
            {/* 네이버 카페 소개 */}
            <TouchableOpacity onPress={() => {
                Linking.openURL("https://cafe.naver.com/uzuhama");
            }} activeOpacity={0.8}>
                <View style={styles.channelInfoContainer}>
                    {assets ? (
                        <Image source={{uri: assets[0].uri}} style={styles.channelThumbnail}/>
                    ) : (
                        <ActivityIndicator size="small" color="#007bff"/>
                    )}
                    <View>
                        <Text style={styles.channelName}>{cafe?.name || "알 수 없음"}</Text>
                        <Text style={styles.channelDescription}>
                            회원 수: {cafe?.members ? cafe.members.toLocaleString() : "정보 없음"}
                        </Text>
                    </View>
                </View>
            </TouchableOpacity>

            <View style={styles.tabsContainer}>
                {tabs.map((tab, index) => (
                    <TouchableOpacity
                        key={index}
                        style={[styles.tabButton, selectedTab === index && styles.selectedTab]}
                        onPress={() => handleTabChange(index)}
                    >
                        <Text style={styles.tabText}>{tab.name}</Text>
                    </TouchableOpacity>
                ))}
            </View>

            <FlatList
                data={tabArticles}
                renderItem={renderItem}
                keyExtractor={(item, index) => index.toString()}
                ListFooterComponent={renderFooter}
                removeClippedSubviews={true}
                initialNumToRender={10}
            />

            <View style={styles.paginationContainer}>
                {renderPageButtons()}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1, // 전체 화면을 채우도록 설정
        padding: 10, // 외부 여백 추가
    },
    channelInfoContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 5,
    },
    channelThumbnail: {
        width: 50,
        height: 50,
        borderRadius: 8,
        marginRight: 15,
    },
    channelName: {
        fontSize: 14,
        fontWeight: 'bold',
    },
    channelDescription: {
        fontSize: 14,
        color: 'gray',
    },
    tabsContainer: {
        flexDirection: 'row',
        marginBottom: 5,
    },
    tabButton: {
        marginRight: 15,
        marginBottom: 5,
        paddingRight: 10,
        borderBottomWidth: 2,
        borderColor: 'transparent',
    },
    selectedTab: {
        borderColor: '#007bff',
    },
    tabText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#007bff',
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
        marginRight: 100, // 타이틀과 아이콘 사이에 여백 추가
    },
    articleMeta: {
        fontSize: 12,
        color: 'gray',
    },
    newIcon: {
        fontSize: 11,
        marginLeft: 1, // 아이콘들 사이의 간격을 최소화
    },
    imageIcon: {
        fontSize: 11,
        marginLeft: 1, // 아이콘들 사이의 간격을 최소화
    },
    footerLoader: {
        marginVertical: 20,
    },
    paginationContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        flexWrap: 'wrap',
        marginTop: 3,
    },
    pageButton: {
        padding: 10,
        marginHorizontal: 5,
    },
    selectedPageButton: {
        backgroundColor: '#f0f0f0',
    },
    pageButtonText: {
        fontSize: 12,
        color: '#333',
    },
});

export default memo(Content);
