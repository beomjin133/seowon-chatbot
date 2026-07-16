import { useState, useEffect } from 'react';

export const useDarkMode = () => {
    // 로컬스토리지에서 다크모드 설정 가져오기
    // 저장된 값이 없으면 무조건 라이트 모드 (false)
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode');
        // 저장된 값이 있으면 그 값 사용, 없으면 false (라이트 모드)
        return saved === 'true';
    });

    useEffect(() => {
        // HTML root 요소에 클래스 추가/제거
        const root = document.documentElement;

        if (isDarkMode) {
            root.classList.add('dark-mode');
        } else {
            root.classList.remove('dark-mode');
        }

        // 로컬스토리지에 저장
        localStorage.setItem('darkMode', isDarkMode.toString());
    }, [isDarkMode]);

    // 다크모드 토글 함수
    const toggleDarkMode = () => {
        setIsDarkMode((prev) => !prev);
    };

    return { isDarkMode, toggleDarkMode };
};