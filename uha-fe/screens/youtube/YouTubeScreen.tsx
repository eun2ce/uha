import React, { useEffect, useState } from "react";
import { ActivityIndicator, Text } from "react-native";
import Content from "./components/Content";

export default function YouTubeScreen() {
    const [channel, setChannel] = useState<any>(null);
    const [readmeContent, setReadmeContent] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(0);
    const [searchDate, setSearchDate] = useState(""); // 검색할 날짜 (YYYY-MM-DD)
    const itemsPerPage = 10; // 한 페이지당 5줄 표시

    const currentYear = new Date().getFullYear(); // 현재 연도

    useEffect(() => {
        fetch("http://127.0.0.1:8000/youtube/channel-info/")
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
        // 기본적으로 현재 연도의 readme 파일을 가져옵니다.
        const fetchReadme = async (year: number) => {
            try {
                const res = await fetch(
                    `https://raw.githubusercontent.com/eun2ce/uzuhama-live-link/main/readme-${year}.md?plain=1`
                );
                const data = await res.text();
                setReadmeContent(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching readme.md:", error);
                setLoading(false);
            }
        };

        fetchReadme(currentYear); // 기본적으로 올해의 readme 파일을 가져옵니다.
    }, [currentYear]);

    if (loading) {
        return <ActivityIndicator />;
    }

    if (!readmeContent) {
        return <Text>Error loading markdown</Text>;
    }

    return (
        <Content
            channel={channel}
            readmeContent={readmeContent}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            searchDate={searchDate}
            setSearchDate={setSearchDate}
            itemsPerPage={itemsPerPage}
        />
    );
}
