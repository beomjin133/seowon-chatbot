import { useState } from 'react';
import { useChat } from '@/modules/chat/chatHooks';
import { useIsMobile } from '@/modules/chat/chatHooks';
import { useDarkMode } from '@/hooks/useDarkMode';
import Header from '@/components/chat/layout/ChatHeader';
import ChatContents from '@/components/chat/layout/ChatContents';
import Bottom from '@/components/chat/layout/ChatBottom';
import SideBar from '@/components/chat/layout/ChatSideBar';
import styles from './ChatPage.module.css';

function ChatPage() {
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const { chatList, chatEndRef, handleSendMessage, loading } = useChat();
    const isMobile = useIsMobile();
    const { isDarkMode, toggleDarkMode } = useDarkMode();

    // 로그인 상태 확인
    const token = localStorage.getItem('token');
    const isLoggedIn = !!token;

    // 사용자 정보
    const user = isLoggedIn
        ? {
            name: '정현영',
            profileImage: '',
        }
        : null;

    // 사이드바 토글
    const toggleSidebar = () => setSidebarOpen((prev) => !prev);

    // 사이드바 외부 클릭 시 닫기
    const handleDimmedClick = () => {
        if (isMobile && isSidebarOpen) {
            setSidebarOpen(false);
        }
    };

    return (
        <div className={styles['page-wrap']}>
            {/* 사이드바 */}
            <SideBar
                isOpen={isSidebarOpen}
                toggleSidebar={toggleSidebar}
                isLoggedIn={isLoggedIn}
                user={user}
                isDarkMode={isDarkMode}
                onToggleDarkMode={toggleDarkMode}
            />

            {/* 모바일 딤드 레이어 */}
            {isMobile && isSidebarOpen && (
                <div
                    className={styles['sidebar-dimmed']}
                    onClick={handleDimmedClick}
                    aria-hidden="true"
                />
            )}

            {/* 메인 채팅 영역 */}
            <div
                className={`${styles['chat-wrap']} ${
                    isSidebarOpen && !isMobile ? styles['shifted'] : ''
                }`}
            >
                <Header
                    toggleSidebar={toggleSidebar}
                    isSidebarOpen={isSidebarOpen}
                />

                <ChatContents
                    chatList={chatList}
                    chatEndRef={chatEndRef}
                />

                <Bottom
                    onSend={handleSendMessage}
                    loading={loading}
                />
            </div>
        </div>
    );
}

export default ChatPage;