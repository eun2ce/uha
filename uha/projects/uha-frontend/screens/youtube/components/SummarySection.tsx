import React, { useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator, Alert, StyleSheet } from "react-native";

interface SummarySectionProps {
    currentYear: number;
    onYearChange: (year: number) => void;
}

interface SummaryData {
    entries: Array<{
        date: string;
        url: string;
    }>;
    summary: string;
    total_streams: number;
    detailed_analysis?: {
        videos: Array<any>;
        summary: string;
        common_keywords: string[];
        total_engagement: {
            total_views: number;
            total_likes: number;
            total_comments: number;
            average_views: number;
        };
    };
    common_keywords?: string[];
    engagement_stats?: {
        total_views: number;
        total_likes: number;
        total_comments: number;
        average_views: number;
    };
}

export default function SummarySection({ currentYear, onYearChange }: SummarySectionProps) {
    const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
    const [loading, setLoading] = useState(false);
    const [showSummary, setShowSummary] = useState(false);
    const [includeDetailedAnalysis, setIncludeDetailedAnalysis] = useState(false);

    const availableYears = [2020, 2021, 2022, 2023, 2024, 2025];

    const fetchSummary = async (year: number) => {
        setLoading(true);
        console.log(`요약 생성 시작: ${year}년`);
        
        try {
            const response = await fetch("http://127.0.0.1:8000/llm/summarize-live-streams", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    year: year,
                    include_detailed_analysis: includeDetailedAnalysis,
                    max_videos_to_analyze: 10
                })
            });

            console.log(`API 응답 상태: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json();
                console.error("API 에러 데이터:", errorData);
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("API 응답 데이터:", data);
            console.log("요약 내용:", data.summary);
            console.log("총 스트림 수:", data.total_streams);
            
            // 요약 데이터 검증
            if (!data.summary || data.summary.trim() === "") {
                throw new Error("요약 데이터가 비어있습니다.");
            }
            
            console.log("setSummaryData 호출 전");
            setSummaryData(data);
            console.log("setShowSummary 호출 전");
            setShowSummary(true);
            console.log("요약 생성 완료! showSummary:", true);
        } catch (error) {
            console.error("Error fetching summary:", error);
            Alert.alert(
                "요약 생성 실패", 
                error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleYearSelect = (year: number) => {
        onYearChange(year);
        if (showSummary) {
            fetchSummary(year);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>라이브 스트림 요약</Text>
                <TouchableOpacity
                    style={[styles.button, loading && styles.buttonDisabled]}
                    onPress={() => fetchSummary(currentYear)}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator size="small" color="#fff" />
                    ) : (
                        <Text style={styles.buttonText}>
                            {currentYear}년 요약 생성
                        </Text>
                    )}
                </TouchableOpacity>
            </View>

            {/* Year Selection */}
            <View style={styles.yearContainer}>
                <Text style={styles.yearLabel}>연도 선택:</Text>
                <View style={styles.yearButtons}>
                    {availableYears.map((year) => (
                        <TouchableOpacity
                            key={year}
                            style={[
                                styles.yearButton,
                                currentYear === year && styles.yearButtonActive
                            ]}
                            onPress={() => handleYearSelect(year)}
                        >
                            <Text style={[
                                styles.yearButtonText,
                                currentYear === year && styles.yearButtonTextActive
                            ]}>
                                {year}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>
            </View>

            {/* Detailed Analysis Option */}
            <View style={styles.optionContainer}>
                <TouchableOpacity
                    style={styles.checkboxContainer}
                    onPress={() => setIncludeDetailedAnalysis(!includeDetailedAnalysis)}
                >
                    <View style={[
                        styles.checkbox,
                        includeDetailedAnalysis && styles.checkboxChecked
                    ]}>
                        {includeDetailedAnalysis && <Text style={styles.checkmark}>✓</Text>}
                    </View>
                    <Text style={styles.optionText}>
                        YouTube 상세 분석 포함 (댓글, 조회수, 키워드)
                    </Text>
                </TouchableOpacity>
                <Text style={styles.optionSubtext}>
                    * API 키 필요, 처리 시간이 더 오래 걸릴 수 있습니다
                </Text>
            </View>

            {/* Summary Display */}
            {console.log("렌더링 시 showSummary:", showSummary, "summaryData:", summaryData)}
            {showSummary && summaryData && (
                <View style={styles.summaryContainer}>
                    <View style={styles.summaryHeader}>
                        <Text style={styles.summaryTitle}>
                            {currentYear}년 라이브 스트림 분석
                        </Text>
                        <Text style={styles.summaryStats}>
                            총 {summaryData.total_streams}회 스트림
                        </Text>
                    </View>
                    
                    <View style={styles.summaryContent}>
                        <Text style={styles.summaryText}>
                            {summaryData.summary}
                        </Text>
                    </View>

                    {/* Detailed Analysis Results */}
                    {summaryData.engagement_stats && (
                        <View style={styles.detailedStatsContainer}>
                            <Text style={styles.detailedStatsTitle}>📊 상세 분석 결과</Text>
                            <View style={styles.statsGrid}>
                                <View style={styles.statItem}>
                                    <Text style={styles.statValue}>
                                        {summaryData.engagement_stats.total_views.toLocaleString()}
                                    </Text>
                                    <Text style={styles.statLabel}>총 조회수</Text>
                                </View>
                                <View style={styles.statItem}>
                                    <Text style={styles.statValue}>
                                        {summaryData.engagement_stats.average_views.toLocaleString()}
                                    </Text>
                                    <Text style={styles.statLabel}>평균 조회수</Text>
                                </View>
                                <View style={styles.statItem}>
                                    <Text style={styles.statValue}>
                                        {summaryData.engagement_stats.total_likes.toLocaleString()}
                                    </Text>
                                    <Text style={styles.statLabel}>총 좋아요</Text>
                                </View>
                                <View style={styles.statItem}>
                                    <Text style={styles.statValue}>
                                        {summaryData.engagement_stats.total_comments.toLocaleString()}
                                    </Text>
                                    <Text style={styles.statLabel}>총 댓글</Text>
                                </View>
                            </View>
                        </View>
                    )}

                    {/* Keywords */}
                    {summaryData.common_keywords && summaryData.common_keywords.length > 0 && (
                        <View style={styles.keywordsContainer}>
                            <Text style={styles.keywordsTitle}>🏷️ 주요 키워드</Text>
                            <View style={styles.keywordsList}>
                                {summaryData.common_keywords.slice(0, 10).map((keyword, index) => (
                                    <View key={index} style={styles.keywordTag}>
                                        <Text style={styles.keywordText}>{keyword}</Text>
                                    </View>
                                ))}
                            </View>
                        </View>
                    )}

                    <TouchableOpacity
                        style={styles.closeButton}
                        onPress={() => setShowSummary(false)}
                    >
                        <Text style={styles.closeButtonText}>닫기</Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 16,
        backgroundColor: "#f8f9fa",
        borderRadius: 8,
        marginVertical: 8,
    },
    header: {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 12,
    },
    title: {
        fontSize: 18,
        fontWeight: "bold",
        color: "#333",
    },
    button: {
        backgroundColor: "#007bff",
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 6,
        minWidth: 120,
        alignItems: "center",
    },
    buttonDisabled: {
        backgroundColor: "#6c757d",
    },
    buttonText: {
        color: "#fff",
        fontWeight: "600",
        fontSize: 14,
    },
    yearContainer: {
        marginBottom: 16,
    },
    yearLabel: {
        fontSize: 14,
        fontWeight: "600",
        color: "#555",
        marginBottom: 8,
    },
    yearButtons: {
        flexDirection: "row",
        flexWrap: "wrap",
        gap: 8,
    },
    yearButton: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 4,
        backgroundColor: "#e9ecef",
        borderWidth: 1,
        borderColor: "#dee2e6",
    },
    yearButtonActive: {
        backgroundColor: "#007bff",
        borderColor: "#007bff",
    },
    yearButtonText: {
        fontSize: 12,
        color: "#495057",
        fontWeight: "500",
    },
    yearButtonTextActive: {
        color: "#fff",
    },
    summaryContainer: {
        backgroundColor: "#fff",
        borderRadius: 8,
        padding: 16,
        borderWidth: 1,
        borderColor: "#dee2e6",
        marginTop: 8,
    },
    summaryHeader: {
        marginBottom: 12,
        paddingBottom: 8,
        borderBottomWidth: 1,
        borderBottomColor: "#e9ecef",
    },
    summaryTitle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#333",
        marginBottom: 4,
    },
    summaryStats: {
        fontSize: 12,
        color: "#6c757d",
    },
    summaryContent: {
        marginBottom: 16,
    },
    summaryText: {
        fontSize: 14,
        lineHeight: 20,
        color: "#495057",
    },
    closeButton: {
        alignSelf: "flex-end",
        paddingHorizontal: 12,
        paddingVertical: 6,
        backgroundColor: "#6c757d",
        borderRadius: 4,
    },
    closeButtonText: {
        color: "#fff",
        fontSize: 12,
        fontWeight: "500",
    },
    // 새로 추가된 스타일들
    optionContainer: {
        marginBottom: 16,
        padding: 12,
        backgroundColor: "#f8f9fa",
        borderRadius: 6,
        borderWidth: 1,
        borderColor: "#e9ecef",
    },
    checkboxContainer: {
        flexDirection: "row",
        alignItems: "center",
        marginBottom: 4,
    },
    checkbox: {
        width: 18,
        height: 18,
        borderWidth: 2,
        borderColor: "#007bff",
        borderRadius: 3,
        marginRight: 8,
        alignItems: "center",
        justifyContent: "center",
    },
    checkboxChecked: {
        backgroundColor: "#007bff",
    },
    checkmark: {
        color: "#fff",
        fontSize: 12,
        fontWeight: "bold",
    },
    optionText: {
        fontSize: 13,
        fontWeight: "500",
        color: "#333",
        flex: 1,
    },
    optionSubtext: {
        fontSize: 11,
        color: "#6c757d",
        fontStyle: "italic",
        marginTop: 2,
    },
    detailedStatsContainer: {
        marginTop: 16,
        padding: 12,
        backgroundColor: "#f8f9fa",
        borderRadius: 6,
        borderWidth: 1,
        borderColor: "#e9ecef",
    },
    detailedStatsTitle: {
        fontSize: 14,
        fontWeight: "bold",
        color: "#333",
        marginBottom: 8,
    },
    statsGrid: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
    },
    statItem: {
        width: "48%",
        alignItems: "center",
        marginBottom: 8,
        padding: 8,
        backgroundColor: "#fff",
        borderRadius: 4,
    },
    statValue: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#007bff",
    },
    statLabel: {
        fontSize: 11,
        color: "#6c757d",
        marginTop: 2,
    },
    keywordsContainer: {
        marginTop: 16,
        padding: 12,
        backgroundColor: "#f8f9fa",
        borderRadius: 6,
        borderWidth: 1,
        borderColor: "#e9ecef",
    },
    keywordsTitle: {
        fontSize: 14,
        fontWeight: "bold",
        color: "#333",
        marginBottom: 8,
    },
    keywordsList: {
        flexDirection: "row",
        flexWrap: "wrap",
        gap: 6,
    },
    keywordTag: {
        backgroundColor: "#007bff",
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
        marginRight: 4,
        marginBottom: 4,
    },
    keywordText: {
        color: "#fff",
        fontSize: 11,
        fontWeight: "500",
    },
});
