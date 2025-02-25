import React, {memo} from "react";
import {Image, Linking, StyleSheet, Text, TextInput, TouchableOpacity, View} from "react-native";
import Markdown from "react-native-markdown-display";

const Content: React.FC<{
    channel: any;
    readmeContent: string | null;
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    endIndex: number;
    filteredLines: string[];
    searchDate: string;
    setSearchDate: React.Dispatch<React.SetStateAction<string>>;
}> = ({channel, readmeContent, currentPage, setCurrentPage, endIndex, filteredLines, searchDate, setSearchDate}) => {
    const totalPages = Math.ceil(filteredLines.length / 5); // 총 페이지 수
    const paginationRange = 5; // 페이지네이션 버튼 수

    // 이전/다음 페이지 버튼 활성화 여부
    const isPrevDisabled = currentPage === 0;
    const isNextDisabled = currentPage === totalPages - 1;

    // 페이지 번호 생성 (1부터 시작)
    const pageNumbers = Array.from({length: Math.min(paginationRange, totalPages)}, (_, index) => index);

    return (
        <View style={styles.container}>
            {/* 채널 정보 */}
            <TouchableOpacity
                onPress={() => Linking.openURL("https://www.youtube.com/@uzuhama")}
                activeOpacity={0.8}
            >
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
            {readmeContent !== undefined && (
                <View style={styles.readmeContainer}>
                    {readmeContent ? (
                        <Markdown>{readmeContent}</Markdown>
                    ) : (
                        <Text>Readme 파일을 불러오는 데 실패했습니다.</Text>
                    )}
                </View>
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
                        <Text
                            style={[
                                styles.pageButton,
                                currentPage === pageNum && styles.selectedPageButton,
                            ]}
                        >
                            {pageNum + 1}
                        </Text>
                    </TouchableOpacity>
                ))}

                {endIndex < filteredLines.length && (
                    <TouchableOpacity
                        onPress={() => setCurrentPage((prev) => prev + 1)}
                    >
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