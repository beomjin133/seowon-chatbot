import { useLogout } from '@/modules/auth/authHooks';
import styles from './LogoutBtn.module.css';

const LogoutBtn = () => {
    const handleLogout = useLogout();
    const token = localStorage.getItem('token');
    const isLoggedIn = !!token;

    // 로그인되어 있지 않으면 렌더링하지 않음
    if (!isLoggedIn) {
        return null;
    }

    return (
        <button
            type="button"
            className={styles['logout-btn']}
            onClick={handleLogout}
            aria-label="로그아웃"
        >
            <svg
                className={styles['logout-icon']}
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span className={styles['logout-text']}>로그아웃</span>
        </button>
    );
};

export default LogoutBtn;