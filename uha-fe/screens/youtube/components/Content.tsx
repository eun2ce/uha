import React from 'react';
import {Image, Linking, StyleSheet, Text, TouchableOpacity, View} from 'react-native';
import Markdown from 'react-native-markdown-display';

interface ContentProps {
    channel: any;
    readmeContent: string | null;
}

const Content: React.FC<ContentProps> = ({channel, readmeContent}) => {
    const handleChannelClick = () => {
        Linking.openURL("https://www.youtube.com/@uzuhama");
    };

    return (
        <View style={styles.container}>
            <View style={styles.cardContainer}>
                {/* YouTube Channel Info Card */}
                <TouchableOpacity style={styles.channelInfoCard} onPress={handleChannelClick}>
                    <View style={styles.channelInfoContainer}>
                        <Image
                            source={{uri: channel?.thumbnail_url || "https://via.placeholder.com/120"}}
                            style={styles.thumbnail}
                        />
                        <View style={styles.textContainer}>
                            <Text style={styles.channelName}>{channel?.channel_name || "알 수 없음"}</Text>
                            <Text style={styles.description}>{channel?.description || "설명 없음"}</Text>
                        </View>
                    </View>
                </TouchableOpacity>

                {/* GitHub Readme.md Display */}
                <View style={styles.readmeContainer}>
                    <Text style={styles.readmeTitle}>GitHub Readme.md</Text>
                    {readmeContent ? (
                        <Markdown style={styles.readmeContent}>{readmeContent}</Markdown>
                    ) : (
                        <Text style={styles.errorText}>Readme 파일을 불러오는 데 실패했습니다.</Text>
                    )}
                </View>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,  // 화면을 꽉 채우도록 설정
        justifyContent: 'center',  // 수직 중앙 정렬
        alignItems: 'center',  // 수평 중앙 정렬
        backgroundColor: '#f5f5f5',  // 배경색
    },
    cardContainer: {
        alignItems: 'center',
        padding: 10,
        backgroundColor: '#fff',
        borderRadius: 10,
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 2},
        shadowOpacity: 0.1,
        shadowRadius: 4,
        marginBottom: 15,
        width: '90%',  // 카드의 너비를 전체 화면에 비해 줄여서 적당한 크기로
    },
    channelInfoCard: {
        width: '100%',
        backgroundColor: '#f9f9f9',
        padding: 10,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 2},
        shadowOpacity: 0.2,
        shadowRadius: 4,
        marginBottom: 10,
        alignItems: 'center',
    },
    channelInfoContainer: {
        flexDirection: 'row',
    },
    thumbnail: {
        width: 100,
        height: 100,
        borderRadius: 50,
        marginRight: 10,
    },
    textContainer: {
        flexDirection: 'column',
        justifyContent: 'center',
    },
    channelName: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    description: {
        fontSize: 12,
        color: 'gray',
        marginTop: 5,
    },
    readmeContainer: {
        marginTop: 20,
        width: '100%',
        alignItems: 'center',
    },
    readmeTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    readmeContent: {
        textAlign: 'center',
        fontSize: 12,
    },
    errorText: {
        color: 'red',
    },
});

export default Content;
