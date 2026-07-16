import React from 'react';
import styles from './DeleteModal.module.css';

const DeleteModal = ({
                         isOpen,
                         onClose,
                         onConfirm,
                         title = '삭제 확인',
                         message = '정말로 삭제하시겠습니까?',
                     }) => {
    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const handleConfirm = () => {
        onConfirm();
        onClose();
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            onClose();
        }
    };

    return (
        <div
            className={styles['modal-overlay']}
            onClick={handleBackdropClick}
            onKeyDown={handleKeyDown}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            aria-describedby="modal-description"
        >
            <div className={styles['modal-container']}>
                {/* 헤더 */}
                <div className={styles['modal-header']}>
                    <div className={styles['modal-icon']}>
                        <svg
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z"
                                fill="#EF4444"
                            />
                        </svg>
                    </div>
                    <h2 id="modal-title" className={styles['modal-title']}>
                        {title}
                    </h2>
                </div>

                {/* 컨텐츠 */}
                <div className={styles['modal-content']}>
                    <p id="modal-description" className={styles['modal-message']}>
                        {message}
                    </p>
                    <div className={styles['modal-warning']}>
                        <svg
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path d="M12 2L2 19H22L12 2Z" fill="#F59E0B" />
                        </svg>
                        <span>삭제하면 되돌릴 수 없습니다.</span>
                    </div>
                </div>

                {/* 액션 버튼 */}
                <div className={styles['modal-actions']}>
                    <button
                        type="button"
                        className={`${styles['modal-btn']} ${styles['btn-cancel']}`}
                        onClick={onClose}
                        aria-label="취소"
                    >
                        취소
                    </button>
                    <button
                        type="button"
                        className={`${styles['modal-btn']} ${styles['btn-confirm']}`}
                        onClick={handleConfirm}
                        aria-label="삭제 확인"
                    >
                        삭제
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteModal;