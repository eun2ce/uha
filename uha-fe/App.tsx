import React, {useEffect, useState} from "react";
import {ActivityIndicator, Image, ScrollView, TouchableOpacity, View} from "react-native";
import {Button, Card, Text} from "react-native-elements";

export default function App() {
    const [channel, setChannel] = useState<any>(null);
    const [cafe, setCafe] = useState<any>(null);
    const [articles, setArticles] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [menuId, setMenuId] = useState(1); // 기본 menu_id (예: 1)
    const [pageId, setPageId] = useState(1); // 기본 page_id (예: 1)

    // YouTube Channel info fetch
    useEffect(() => {
        fetch("http://127.0.0.1:8000/youtube/channel-info")
            .then((res) => res.json())
            .then((data) => {
                setChannel(data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching channel info:", error);
                setLoading(false);
            });
    }, []);

    // Naver Cafe info fetch
    useEffect(() => {
        fetch("http://127.0.0.1:8000/naver-cafe/profile/")
            .then((res) => res.json())
            .then((data) => {
                setCafe(data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching cafe info:", error);
                setLoading(false);
            });
    }, []);

    // Naver Cafe articles fetch
    useEffect(() => {
        setLoading(true); // 데이터 로딩 시작
        fetch(`http://127.0.0.1:8000/naver-cafe/articles/${menuId}/${pageId}/`)
            .then((res) => res.json())
            .then((data) => {
                setArticles(data.result || []);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching articles:", error);
                setLoading(false);
            });
    }, [menuId, pageId]); // menuId와 pageId가 변경될 때마다 데이터 다시 가져오기

    if (loading) {
        return (
            <View style={{flex: 1, justifyContent: "center", alignItems: "center"}}>
                <ActivityIndicator size="large" color="#0000ff"/>
            </View>
        );
    }

    if (!channel || !cafe) return null; // 채널 정보나 카페 정보가 없으면 화면에 아무것도 표시하지 않음

    return (
        <ScrollView contentContainerStyle={{padding: 20}}>
            <Card containerStyle={{width: "100%", alignItems: "center"}}>
                {/* YouTube Channel Info */}
                <Image
                    source={{uri: channel.thumbnail_url || "https://via.placeholder.com/120"}}
                    style={{width: 120, height: 120, borderRadius: 60, marginBottom: 10}}
                />
                <Text h4>{channel.channel_name || "알 수 없음"}</Text>
                <Text>@{channel.custom_url || "없음"}</Text>
                <Text style={{marginVertical: 10}}>{channel.description || "설명 없음"}</Text>
                <Text>구독자
                    수: {channel.subscriber_count ? parseInt(channel.subscriber_count).toLocaleString() + "명" : "정보 없음"}</Text>
                <Text>총 조회수: {channel.view_count ? parseInt(channel.view_count).toLocaleString() + "회" : "정보 없음"}</Text>
                <Text>업로드한 영상: {channel.video_count || "0"}개</Text>
                <Text>개설일: {channel.published_at ? new Date(channel.published_at).toLocaleDateString() : "정보 없음"}</Text>

                {/* Naver Cafe Info */}
                <View style={{marginTop: 30}}>
                    <Image
                        source={{uri: cafe.thumbnail}}
                        style={{width: 120, height: 120, borderRadius: 60, marginBottom: 10}}
                    />
                    <Text h4>{cafe.name || "알 수 없음"}</Text>
                    <Text>회원 수: {cafe.members ? cafe.members.toLocaleString() : "정보 없음"}</Text>
                </View>

                {/* Naver Cafe Articles */}
                <View style={{marginTop: 30}}>
                    <Text h4>게시글 목록</Text>
                    {articles.length > 0 ? (
                        articles.map((article, index) => (
                            <View key={index} style={{marginBottom: 10}}>
                                <TouchableOpacity onPress={() => window.open(article.link, "_blank")}>
                                    <View style={{
                                        flexDirection: "row",
                                        justifyContent: "space-between",
                                        alignItems: "center"
                                    }}>
                                        <Text h5 style={{fontWeight: "bold", flex: 1}}>
                                            {article.title}
                                        </Text>
                                        <Text style={{fontSize: 12, color: "gray"}}>
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
                    <View style={{flexDirection: "row", marginTop: 20}}>
                        <Button
                            title="이전"
                            onPress={() => setPageId(pageId > 1 ? pageId - 1 : 1)}
                            disabled={pageId <= 1}
                            buttonStyle={{marginRight: 10}}
                        />
                        <Button
                            title="다음"
                            onPress={() => setPageId(pageId + 1)}
                        />
                    </View>
                </View>
            </Card>
        </ScrollView>
    );
}
