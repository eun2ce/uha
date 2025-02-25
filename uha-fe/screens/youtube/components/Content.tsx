import React, { memo, useEffect, useState } from "react";
import { Image, Linking, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import Markdown from "react-native-markdown-display";

// 연도별로 readme 파일을 가져오는 함수
const fetchReadmeFile = async (year: string) => {
    try {
        const response = await fetch(`https://raw.githubusercontent.com/eun2ce/uzuhama-live-link/main/readme-${year}.md?plain=1`);
        const content = await response.text();
        return content;
    } catch (error) {
        console.error("Error loading readme file:", error);
        return "";
    }
};

const Content: React.FC<{
    channel: any;
    readmeContent: string;
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    searchDate: string;
    setSearchDate: React.Dispatch<React.SetStateAction<string>>;
    itemsPerPage: number;
}> = ({ channel, readmeContent, currentPage, setCurrentPage, searchDate, setSearchDate, itemsPerPage }) => {
    const [filteredContent, setFilteredContent] = useState<string>("");

    // 검색된 연도에 맞는 readme 파일을 가져오는 함수
    useEffect(() => {
        const fetchFilteredReadme = async () => {
            let year = new Date().getFullYear().toString(); // 기본값은 올해
            if (searchDate) {
                year = searchDate.slice(0, 4); // YYYY 형식으로 연도만 추출
            }
            const content = await fetchReadmeFile(year); // 해당 연도의 readme 파일을 가져옴
            setFilteredContent(content);
        };

        fetchFilteredReadme();
    }, [searchDate]);

    const lines = filteredContent.split("\n");
    const tableHeaderAndSecondLine = lines.slice(0, 2); // 표 헤더와 두 번째 라인
    const contentLines = lines.slice(2); // 실제 내용

    // 날짜 검색 처리 (YYYY-MM-DD 형식)
    const filteredLines = searchDate
        ? contentLines.filter((line) => {
            // 날짜 형식 추출 (YYYY-MM-DD)
            const dateRegex = new RegExp(`\\d{4}-${searchDate.slice(5, 7)}-${searchDate.slice(8, 10)}`, "g");
            return dateRegex.test(line);
        })
        : contentLines;

    const startIndex = currentPage * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedContent = [...tableHeaderAndSecondLine, ...filteredLines.slice(startIndex, endIndex)].join("\n");

    const totalPages = Math.ceil(filteredLines.length / itemsPerPage); // 총 페이지 수

    // 페이지 번호 생성 (1부터 시작)
    const pageNumbers = Array.from({ length: Math.min(5, totalPages) }, (_, index) => index);

    return (
        <View style={styles.container}>
            {/* 채널 정보 */}
            <TouchableOpacity onPress={() => Linking.openURL("https://www.youtube.com/@uzuhama")} activeOpacity={0.8}>
                <View style={styles.channelInfoContainer}>
                    <Image
                        source={{ uri: channel?.thumbnail_url || "https://via.placeholder.com/120" }}
                        style={styles.channelThumbnail}
                    />
                    <View>
                        <Text style={styles.channelName}>{channel?.channel_name || "알 수 없음"}</Text>
                        <Text style={styles.channelDescription}>{channel?.description || "설명 없음"}</Text>
                    </View>
                </View>
            </TouchableOpacity>

            {/* 날짜 검색 입력창 */}
            <TextInput
                style={styles.dateInput}
                placeholder="YYYY-MM-DD 형식으로 날짜 입력"
                value={searchDate}
                onChangeText={(text) => {
                    setSearchDate(text);
                    setCurrentPage(0); // 검색할 때 첫 페이지로 이동
                }}
            />

            {/* Readme 내용 */}
            {paginatedContent ? (
                <View style={styles.readmeContainer}>
                    <Markdown>{paginatedContent}</Markdown>
                </View>
            ) : (
                <Text>Readme 파일을 불러오는 데 실패했습니다.</Text>
            )}

            {/* 페이지네이션 버튼 */}
            <View style={styles.paginationContainer}>
                {currentPage > 0 && (
                    <TouchableOpacity onPress={() => setCurrentPage((prev) => Math.max(prev - 1, 0))}>
                        <Text style={styles.pageButton}>{'<'}</Text>
                    </TouchableOpacity>
                )}

                {pageNumbers.map((pageNum) => (
                    <TouchableOpacity key={pageNum} onPress={() => setCurrentPage(pageNum)}>
                        <Text style={[styles.pageButton, currentPage === pageNum && styles.selectedPageButton]}>
                            {pageNum + 1}
                        </Text>
                    </TouchableOpacity>
                ))}

                {currentPage < totalPages - 1 && (
                    <TouchableOpacity onPress={() => setCurrentPage((prev) => prev + 1)}>
                        <Text style={styles.pageButton}>{'>'}</Text>
                    </TouchableOpacity>
                )}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 10,
    },
    dateInput: {
        height: 40,
        borderColor: "gray",
        borderWidth: 1,
        marginBottom: 10,
        paddingHorizontal: 8,
        borderRadius: 5,
    },
    channelInfoContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    channelThumbnail: {
        width: 60,
        height: 60,
        borderRadius: 30,
        borderWidth: 2,
        borderColor: 'white',
    },
    channelName: {
        fontWeight: 'bold',
        marginLeft: 10,
    },
    channelDescription: {
        marginLeft: 10,
        marginTop: 5,
        color: 'gray',
    },
    readmeContainer: {
        marginTop: 5,
    },
    paginationContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        flexWrap: 'wrap',
        marginTop: 3,
    },
    pageButton: {
        padding: 5,
        marginHorizontal: 5,
    },
    selectedPageButton: {
        backgroundColor: '#f0f0f0',
    },
});

export default memo(Content);
