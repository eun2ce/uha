import React, {useEffect, useState} from "react";
import {ActivityIndicator, ScrollView, View} from "react-native";
import Content from "./components/Content";

export default function CafeScreen() {
    const [cafe, setCafe] = useState<any>(null);
    const [articles, setArticles] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [menuId, setMenuId] = useState(1);
    const [pageId, setPageId] = useState(1);

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

    useEffect(() => {
        setLoading(true);
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
    }, [menuId, pageId]);

    const handleArticlePress = (link: string) => {
        window.open(link, "_blank");
    };

    const handlePageChange = (direction: string) => {
        if (direction === "previous" && pageId > 1) {
            setPageId(pageId - 1);
        } else if (direction === "next") {
            setPageId(pageId + 1);
        }
    };

    if (loading) {
        return (
            <View style={{flex: 1, justifyContent: "center", alignItems: "center"}}>
                <ActivityIndicator size="large" color="#0000ff"/>
            </View>
        );
    }

    return (
        <ScrollView contentContainerStyle={{padding: 20}}>
            <Content
                cafe={cafe}
                articles={articles}
                onArticlePress={handleArticlePress}
                onPageChange={handlePageChange}
                pageId={pageId}
            />
        </ScrollView>
    );
}
