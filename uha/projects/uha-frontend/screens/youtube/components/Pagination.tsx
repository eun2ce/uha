import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
    if (totalPages <= 1) return null;

    const getPageNumbers = () => {
        const pages = [];
        const maxVisiblePages = 5;
        
        if (totalPages <= maxVisiblePages) {
            // Show all pages if total is small
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            // Show smart pagination
            if (currentPage <= 3) {
                // Show first pages
                for (let i = 1; i <= 4; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            } else if (currentPage >= totalPages - 2) {
                // Show last pages
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 3; i <= totalPages; i++) {
                    pages.push(i);
                }
            } else {
                // Show middle pages
                pages.push(1);
                pages.push('...');
                for (let i = currentPage - 1; i <= currentPage + 1; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            }
        }
        
        return pages;
    };

    const handlePrevious = () => {
        if (currentPage > 1) {
            onPageChange(currentPage - 1);
        }
    };

    const handleNext = () => {
        if (currentPage < totalPages) {
            onPageChange(currentPage + 1);
        }
    };

    const handlePagePress = (page: number | string) => {
        if (typeof page === 'number' && page !== currentPage) {
            onPageChange(page);
        }
    };

    return (
        <View style={styles.container}>
            {/* Previous Button */}
            <TouchableOpacity
                style={[
                    styles.button,
                    styles.navButton,
                    currentPage === 1 && styles.disabledButton
                ]}
                onPress={handlePrevious}
                disabled={currentPage === 1}
            >
                <Text style={[
                    styles.buttonText,
                    styles.navButtonText,
                    currentPage === 1 && styles.disabledText
                ]}>
                    ‹
                </Text>
            </TouchableOpacity>

            {/* Page Numbers */}
            <View style={styles.pagesContainer}>
                {getPageNumbers().map((page, index) => (
                    <TouchableOpacity
                        key={index}
                        style={[
                            styles.button,
                            styles.pageButton,
                            page === currentPage && styles.activeButton,
                            page === '...' && styles.ellipsisButton
                        ]}
                        onPress={() => handlePagePress(page)}
                        disabled={page === '...' || page === currentPage}
                    >
                        <Text style={[
                            styles.buttonText,
                            styles.pageButtonText,
                            page === currentPage && styles.activeText,
                            page === '...' && styles.ellipsisText
                        ]}>
                            {page}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            {/* Next Button */}
            <TouchableOpacity
                style={[
                    styles.button,
                    styles.navButton,
                    currentPage === totalPages && styles.disabledButton
                ]}
                onPress={handleNext}
                disabled={currentPage === totalPages}
            >
                <Text style={[
                    styles.buttonText,
                    styles.navButtonText,
                    currentPage === totalPages && styles.disabledText
                ]}>
                    ›
                </Text>
            </TouchableOpacity>

            {/* Page Info */}
            <View style={styles.pageInfo}>
                <Text style={styles.pageInfoText}>
                    {currentPage} / {totalPages}
                </Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 20,
        paddingHorizontal: 16,
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: '#e9ecef',
    },
    pagesContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginHorizontal: 8,
    },
    button: {
        minWidth: 40,
        height: 40,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 8,
        marginHorizontal: 2,
    },
    navButton: {
        backgroundColor: '#f8f9fa',
        borderWidth: 1,
        borderColor: '#dee2e6',
    },
    pageButton: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#dee2e6',
    },
    activeButton: {
        backgroundColor: '#007bff',
        borderColor: '#007bff',
    },
    disabledButton: {
        backgroundColor: '#f8f9fa',
        borderColor: '#dee2e6',
        opacity: 0.5,
    },
    ellipsisButton: {
        backgroundColor: 'transparent',
        borderColor: 'transparent',
    },
    buttonText: {
        fontSize: 14,
        fontWeight: '500',
    },
    navButtonText: {
        color: '#6c757d',
        fontSize: 18,
        fontWeight: '600',
    },
    pageButtonText: {
        color: '#333',
    },
    activeText: {
        color: '#fff',
    },
    disabledText: {
        color: '#adb5bd',
    },
    ellipsisText: {
        color: '#6c757d',
    },
    pageInfo: {
        marginLeft: 16,
        paddingHorizontal: 12,
        paddingVertical: 6,
        backgroundColor: '#f8f9fa',
        borderRadius: 6,
    },
    pageInfoText: {
        fontSize: 12,
        color: '#6c757d',
        fontWeight: '500',
    },
});
