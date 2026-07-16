import { useEffect } from 'react';
import ChatBubble from '../ui/ChatBubble';
import styles from './ChatContents.module.css';

const ChatContents = ({ chatList, chatEndRef }) => {
    // 새 메시지가 추가될 때마다 스크롤을 맨 아래로
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatList, chatEndRef]);

    return (
        <div className={styles['chat-container']}>
            <div className={styles['chat-inner']}>
                <div className={styles['chat-content']}>
                    {/* 채팅 리스트가 비어있을 때 환영 메시지 */}
                    {chatList.length === 0 && (
                        <div className={styles['welcome-message']}>
                            <div className={styles['welcome-icon']}>
                                <span className="ico-logo logo-blue" />
                            </div>
                            <h2 className={styles['welcome-title']}>S-Goon에 오신 것을 환영합니다</h2>
                            <p className={styles['welcome-text']}>
                                무엇이든 물어보세요. 최선을 다해 도와드리겠습니다.
                            </p>
                        </div>
                    )}

                    {/* 채팅 메시지 목록 */}
                    {chatList.map((msg, index) => (
                        <ChatBubble
                            key={`${msg.type}-${index}`}
                            type={msg.type}
                            text={msg.text}
                            spinner={
                                msg.type === 'loading'
                                    ? require('@/assets/icons/spinner.png')
                                    : null
                            }
                        />
                    ))}

                    {/* 스크롤 타겟 */}
                    <div ref={chatEndRef} className={styles['scroll-anchor']} />
                </div>
            </div>
        </div>
    );
};

export default ChatContents;