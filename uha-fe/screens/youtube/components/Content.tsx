import React, {memo, useEffect, useState} from "react";
import {Image, Linking, StyleSheet, Text, TextInput, TouchableOpacity, View} from "react-native";
import Markdown from "react-native-markdown-display";

// readme-{YYYY}.md 파일을 불러오는 예시 (예시로 static 파일을 사용하는 경우, 실제로는 API 호출을 사용할 수 있음)
const fetchReadmeFile = async (year: string) => {
    // 예시로, 연도에 맞는 readme 파일을 로드하는 로직
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
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    searchDate: string;
    setSearchDate: React.Dispatch<React.SetStateAction<string>>;
    itemsPerPage: number;
}> = ({channel, currentPage, setCurrentPage, searchDate, setSearchDate, itemsPerPage}) => {
    const [readmeContent, setReadmeContent] = useState<string>("");

    // 연도에 맞는 readme 파일을 불러오는 useEffect
    useEffect(() => {
        const year = searchDate.split("-")[0]; // YYYY만 추출
        if (year) {
            fetchReadmeFile(year).then(setReadmeContent);
        }
    }, [searchDate]);

    const lines = readmeContent.split("\n");
    const tableHeaderAndSecondLine = lines.slice(0, 2);
    const contentLines = lines.slice(2);

    // 날짜 검색 처리 (검색 시 연도 상관없이)
    const filteredLines = searchDate
        ? contentLines.filter((line) => line.includes(searchDate)) // 검색 날짜 포함 여부 체크
        : contentLines;

    const startIndex = currentPage * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedContent = [...tableHeaderAndSecondLine, ...filteredLines.slice(startIndex, endIndex)].join("\n");

    const totalPages = Math.ceil(filteredLines.length / itemsPerPage); // 총 페이지 수

    // 페이지 번호 생성 (1부터 시작)
    const pageNumbers = Array.from({length: Math.min(5, totalPages)}, (_, index) => index);

    return (
        <View style={styles.container}>
            {/* 채널 정보 */}
            <TouchableOpacity onPress={() => Linking.openURL("https://www.youtube.com/@uzuhama")} activeOpacity={0.8}>
                <View style={styles.channelInfoContainer}>
                    <Image
                        source={{uri: channel?.thumbnail_url || "https://via.placeholder.com/120"}}
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
