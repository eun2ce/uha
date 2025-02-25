// Header.tsx
import React from 'react';
import {Image, StyleSheet, View} from 'react-native';

const Header: React.FC = () => {
    return (
        <View style={styles.header}>
            <Image
                source={{uri: 'https://yt3.googleusercontent.com/396QpZsH0bMlwH9ybWYIysjpkBDS-VB_7Rmnqy_MIfU_8fx89Twtp4rCXsWVpRo3bYpiwjLhPQ=w2276-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj'}}
                style={styles.headerImage}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    header: {
        height: 300, // 헤더 이미지의 높이 설정
        width: '100%',
        overflow: 'hidden', // 이미지가 화면 밖으로 넘어가지 않도록 설정
    },
    headerImage: {
        width: '100%',
        height: '100%',
        resizeMode: 'cover', // 이미지가 영역을 덮도록 설정
    },
});

export default Header;
