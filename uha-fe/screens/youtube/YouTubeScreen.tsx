import React, { useEffect, useState } from "react";
import { ActivityIndicator, ScrollView, View } from "react-native";
import Content from "./components/Content";

export default function YouTubeScreen() {
    const [channel, setChannel] = useState<any>(null);
    const [readmeContent, setReadmeContent] = useState(null);
    const [loading, setLoading] = useState(true);

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

    useEffect(() => {
        fetch("https://raw.githubusercontent.com/eun2ce/uzuhama-live-link/main/readme.md?plain=1")
            .then((res) => res.text())
            .then((data) => {
                setReadmeContent(data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching readme.md:", error);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                <ActivityIndicator size="large" color="#0000ff" />
            </View>
        );
    }

    return (
        <ScrollView contentContainerStyle={{ padding: 20 }}>
            <Content channel={channel} readmeContent={readmeContent} />
        </ScrollView>
    );
}
