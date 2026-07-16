import { memo } from 'react';
import styles from './ChatBubble.module.css';
import spinner from '@/assets/icons/spinner.png';

const ChatBubble = ({ type, text, spinner: customSpinner }) => {
    const isUser = type === 'user';
    const isBot = type === 'bot';
    const isLoading = type === 'loading';
    const isError = type === 'error';

    // 사용자 메시지
    if (isUser) {
        return (
            <div className={styles['user-wrap']}>
                <div className={styles['user-bubble']}>
                    <div className={styles['user-chating']}>
            <span className={styles['user-text']}>
              {typeof text === 'object' ? text.message : text}
            </span>
                    </div>
                </div>
            </div>
        );
    }

    // 봇 메시지, 로딩, 에러
    if (isBot || isLoading || isError) {
        return (
            <div className={styles['bot-wrap']}>
                <div className={styles['bot-profile']}>
                    <div className={styles['ico-bot-profile']}>
            <span className={styles['ico-bot-logo']}>
              {isError ? '⚠️' : '🤖'}
            </span>
                    </div>
                </div>
                <div className={styles['bot-content']}>
                    <div className={styles['bot-name-wrap']}>
            <span className={styles['bot-name']}>
              {isError ? 'System' : 'S-Goon'}
            </span>
                    </div>
                    <div
                        className={`${styles['bot-bubble']} ${
                            isError ? styles['error-bubble'] : ''
                        } ${isLoading ? styles['loading-bubble'] : ''}`}
                    >
                        <div className={styles['bot-chating']}>
                            {/* 로딩 스피너 */}
                            {(isLoading || customSpinner) && (
                                <img
                                    src={spinner}
                                    alt="로딩 중"
                                    className={styles['spinner']}
                                />
                            )}

                            {/* 텍스트 */}
                            <span
                                className={`${styles['bot-text']} ${
                                    isError ? styles['error-text'] : ''
                                } ${isLoading ? styles['loading-text'] : ''}`}
                            >
                {text?.message || text || '응답을 생성하고 있습니다...'}
              </span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return null;
};

// 메모이제이션으로 불필요한 리렌더링 방지
export default memo(ChatBubble);