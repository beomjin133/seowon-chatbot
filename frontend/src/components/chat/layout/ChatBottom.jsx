import { useState, useRef, useEffect } from 'react';
import { SendIcon } from '@/assets/icons/Icons';
import styles from './ChatBottom.module.css';

function Bottom({ onSend, loading }) {
    const [input, setInput] = useState('');
    const textareaRef = useRef(null);

    // textarea 높이 자동 조절
    const resizeTextarea = () => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    };

    // 입력값 변경 처리
    const handleChange = (e) => {
        setInput(e.target.value);
        resizeTextarea();
    };

    // 메시지 전송 처리
    const handleSubmit = () => {
        if (!input.trim() || loading) return; // 공백이거나 로딩 중일 때 무시

        onSend(input.trim()); // 상위 컴포넌트에 메시지 전달
        setInput(''); // 입력창 초기화

        // textarea 높이 초기화
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    // 키보드 이벤트 처리
    const handleKeyDown = (e) => {
        // Enter: 전송, Shift + Enter: 줄바꿈
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    // 컴포넌트 마운트 시 textarea 높이 설정
    useEffect(() => {
        resizeTextarea();
    }, []);

    // 로딩 중일 때 포커스 해제
    useEffect(() => {
        if (loading && textareaRef.current) {
            textareaRef.current.blur();
        }
    }, [loading]);

    return (
        <div className={styles['chat-bottom']}>
            <div className={styles['inp-wrap']}>
                <div className={styles['inp-box']}>
                    {/* 텍스트 입력 영역 */}
                    <div className={styles['inp-text-wrap']}>
            <textarea
                ref={textareaRef}
                className={styles['inp-text']}
                placeholder="질문을 입력하세요."
                value={input}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={loading}
                aria-label="채팅 입력창"
                aria-disabled={loading}
            />
                    </div>

                    {/* 액션 버튼 영역 */}
                    <div className={styles['inp-actions-wrap']}>
                        {/* 기능 버튼들 (추후 구현) */}
                        <div className={styles['inp-functions-wrap']}>
                            <button
                                type="button"
                                className={styles['icon-btn']}
                                disabled={loading}
                                aria-label="파일 추가"
                            >
                                <span className="ico-add"></span>
                            </button>
                            <button
                                type="button"
                                className={styles['icon-btn']}
                                disabled={loading}
                                aria-label="언어 설정"
                            >
                                <span className="ico-lang"></span>
                            </button>
                            <button
                                type="button"
                                className={styles['icon-btn']}
                                disabled={loading}
                                aria-label="더보기"
                            >
                                <span className="ico-more"></span>
                            </button>
                        </div>

                        {/* 전송 버튼 */}
                        <button
                            type="button"
                            className={`btn-ico ${styles['send-btn']} ${
                                loading ? styles['loading'] : ''
                            }`}
                            onClick={handleSubmit}
                            disabled={loading || !input.trim()}
                            aria-label={loading ? '전송 중...' : '메시지 전송'}
                        >
                            <SendIcon color="var(--ico-color-primary)" />
                        </button>
                    </div>
                </div>
            </div>

            {/* 경고 문구 */}
            <div className={styles['inp-warning']}>
                <p>S-Goon은 테스트 단계입니다. 부정확한 정보를 제공할 수 있습니다.</p>
            </div>
        </div>
    );
}

export default Bottom;