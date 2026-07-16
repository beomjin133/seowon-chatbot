import React from 'react';
import { SidebarIcon, HelpIcon } from '@/assets/icons/Icons';
import styles from './ChatHeader.module.css';

function Header({ toggleSidebar, isSidebarOpen }) {
    return (
        <header className={styles['chat-header']}>
            {/* 사이드바 토글 버튼 */}
            <button
                type="button"
                className={`btn-ico ${isSidebarOpen ? styles['hide-btn'] : ''}`}
                onClick={toggleSidebar}
                disabled={isSidebarOpen}
                aria-label="사이드바 열기"
                aria-expanded={isSidebarOpen}
            >
                <SidebarIcon color="var(--ico-color-primary)" />
            </button>

            {/* 로고 */}
            <h1 className={styles['h-tit']}>
                <span className="ico-logo logo-blue" aria-label="S-Goon 로고" />
            </h1>

            {/* 도움말 버튼 */}
            <button
                type="button"
                className="btn-ico"
                aria-label="도움말"
            >
                <HelpIcon color="var(--ico-color-primary)" />
            </button>
        </header>
    );
}

export default Header;