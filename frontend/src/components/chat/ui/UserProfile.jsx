import { jwtDecode } from 'jwt-decode';
import { useNavigate } from 'react-router-dom';
import styles from './UserProfile.module.css';

const UserProfile = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    let userName = '로그인 해주세요';
    let userInitial = '?';
    const isLoggedIn = !!token;

    // 토큰에서 사용자 정보 추출
    if (token) {
        try {
            const decoded = jwtDecode(token);
            userName = decoded.user_name || decoded.name || '사용자';
            // 이름의 첫 글자를 아바타로 사용
            userInitial = userName.charAt(0).toUpperCase();
        } catch (e) {
            console.error('❌ JWT 디코딩 실패:', e);
        }
    }

    const handleClick = () => {
        if (!isLoggedIn) {
            navigate('/auth/login');
        }
    };

    return (
        <div
            className={`${styles['profile-container']} ${
                !isLoggedIn ? styles['clickable'] : ''
            }`}
            onClick={handleClick}
            role={!isLoggedIn ? 'button' : undefined}
            aria-label={!isLoggedIn ? '로그인 페이지로 이동' : undefined}
            tabIndex={!isLoggedIn ? 0 : undefined}
        >
            {/* 아바타 */}
            <div
                className={`${styles['profile-avatar']} ${
                    isLoggedIn ? styles['logged-in'] : styles['logged-out']
                }`}
            >
                <span className={styles['profile-initial']}>{userInitial}</span>
            </div>

            {/* 사용자 정보 */}
            <div className={styles['profile-info']}>
                <p className={styles['profile-name']}>{userName}</p>
                {isLoggedIn && (
                    <span className={styles['profile-status']}>온라인</span>
                )}
            </div>
        </div>
    );
};

export default UserProfile;