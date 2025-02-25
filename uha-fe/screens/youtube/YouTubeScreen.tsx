import React, { useEffect, useState } from "react";
import { ActivityIndicator, ScrollView, Text, TextInput, View } from "react-native";
import Content from "./components/Content";

export default function YouTubeScreen() {
    const [channel, setChannel] = useState<any>(null);
    const [readmeContent, setReadmeContent] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(0);
    const [searchDate, setSearchDate] = useState(""); // 검색할 날짜 (YYYY-MM-DD)
    const itemsPerPage = 5; // 한 페이지당 5줄 표시

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
        return <ActivityIndicator />;
    }

    if (!readmeContent) {
        return <Text>Error loading markdown</Text>;
    }

    // 마크다운을 줄 단위로 나누기
    const lines = readmeContent.split("\n");
    const tableHeaderAndSecondLine = lines.slice(0, 2);
    const contentLines = lines.slice(2);
    const filteredLines = searchDate
        ? contentLines.filter((line) => line.includes(searchDate))
        : contentLines;

    const startIndex = currentPage * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedContent = [...tableHeaderAndSecondLine, ...filteredLines.slice(startIndex, endIndex)].join("\n");

    return (
        <Content
            channel={channel}
            readmeContent={paginatedContent}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            endIndex={endIndex}
            filteredLines={filteredLines}
            searchDate={searchDate}
            setSearchDate={setSearchDate}
        />
    );
}
