import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    selectRoom,
    startNewChat,
    fetchChatHistory,
    deleteChatRoom,
    updateChatRoomTitle,
} from '@/modules/chat/slices/chatSlice';
import UserProfile from '../ui/UserProfile';
import LogoutBtn from '../ui/LogoutBtn';
import DarkModeToggle from '../ui/DarkModeToggle';
import DeleteModal from '../ui/DeleteModal';
import { SidebarIcon, PlusIcon } from '@/assets/icons/Icons';
import styles from './ChatSideBar.module.css';

// 수정 아이콘 SVG
const EditIcon = ({ size = 16, color = 'currentColor' }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
    >
        <path
            d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
        <path
            d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
    </svg>
);

// 삭제 아이콘 SVG
const DeleteIcon = ({ size = 16, color = 'currentColor' }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
    >
        <path
            d="M3 6H5H21"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
        <path
            d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
        <path
            d="M10 11V17"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
        <path
            d="M14 11V17"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
    </svg>
);

function SideBar({
                     isOpen,
                     toggleSidebar,
                     isLoggedIn,
                     user,
                     isDarkMode,
                     onToggleDarkMode
                 }) {
    const dispatch = useDispatch();
    const rooms = useSelector((state) => state.chat.rooms);
    const selectedRoomId = useSelector((state) => state.chat.selectedRoomId);

    // 삭제 모달 상태
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [roomToDelete, setRoomToDelete] = useState(null);

    // 채팅방 선택
    const handleRoomClick = (roomId) => {
        console.log('Selected Room ID:', roomId);
        dispatch(selectRoom(roomId));
        dispatch(fetchChatHistory(roomId));
    };

    // 새 채팅 시작 (+ 버튼 클릭) - 빈 채팅방으로 이동
    const handleAddRoom = () => {
        dispatch(startNewChat());
    };

    // 채팅방 삭제 - 모달 열기
    const handleDeleteRoomClick = (room) => {
        setRoomToDelete(room);
        setIsDeleteModalOpen(true);
    };

    // 채팅방 삭제 확인
    const handleConfirmDelete = () => {
        if (roomToDelete) {
            dispatch(deleteChatRoom(roomToDelete.id));
            setRoomToDelete(null);
        }
    };

    // 채팅방 이름 수정
    const handleEditRoom = (roomId, currentTitle) => {
        const newTitle = prompt('새 채팅방 이름을 입력하세요', currentTitle);
        if (newTitle?.trim() && newTitle.trim() !== currentTitle) {
            dispatch(
                updateChatRoomTitle({ sessionId: roomId, newTitle: newTitle.trim() })
            );
        }
    };

    return (
        <>
            <aside
                className={`${styles['sidebar-overlay']} ${isOpen ? styles['open'] : ''}`}
                onClick={(e) => e.stopPropagation()}
                aria-hidden={!isOpen}
            >
                {/* 사이드바 헤더 */}
                <div className={styles['sidebar-header']}>
                    <button
                        type="button"
                        className="btn-ico"
                        onClick={toggleSidebar}
                        aria-label="사이드바 닫기"
                    >
                        <SidebarIcon color="var(--ico-color-primary)" />
                    </button>

                    {/* 빈 공간 (레이아웃 균형) */}
                    <div className={styles['header-spacer']}></div>
                </div>

                {/* 사이드바 콘텐츠 */}
                <div className={styles['sidebar-content']}>
                    <ul className={styles['sidebar-list']}>
                        {/* 사용자 프로필 */}
                        <li>
                            <UserProfile isLoggedIn={isLoggedIn} user={user} />
                        </li>

                        {/* 채팅방 목록 - 로그인 상태일 때만 표시 */}
                        {isLoggedIn && (
                            <li className={styles['room-list-section']}>
                                {/* 채팅 기록 헤더 (제목 + 추가 버튼) */}
                                <div className={styles['section-header']}>
                                    <h3 className={styles['section-title']}>채팅 기록</h3>
                                    <button
                                        type="button"
                                        className={styles['add-room-btn']}
                                        onClick={handleAddRoom}
                                        aria-label="새 채팅 시작"
                                        title="새 채팅"
                                    >
                                        <PlusIcon color="var(--ico-color-primary)" />
                                    </button>
                                </div>

                                {/* 채팅방 목록 */}
                                {rooms.length === 0 ? (
                                    <div className={styles['empty-state']}>
                                        <p>채팅 기록이 없습니다</p>
                                        <button
                                            type="button"
                                            className={styles['create-room-btn']}
                                            onClick={handleAddRoom}
                                        >
                                            새 채팅 시작하기
                                        </button>
                                    </div>
                                ) : (
                                    <ul className={styles['room-list']}>
                                        {rooms.map((room) => (
                                            <li
                                                key={room.id}
                                                className={`${styles['room-item']} ${
                                                    selectedRoomId === room.id ? styles['active'] : ''
                                                }`}
                                            >
                                                <button
                                                    type="button"
                                                    className={styles['room-button']}
                                                    onClick={() => handleRoomClick(room.id)}
                                                    aria-current={
                                                        selectedRoomId === room.id ? 'page' : undefined
                                                    }
                                                >
                                                    <span className={styles['room-title']}>
                                                        {room.title}
                                                    </span>
                                                </button>

                                                <div className={styles['room-actions']}>
                                                    <button
                                                        type="button"
                                                        className={styles['action-button']}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleEditRoom(room.id, room.title);
                                                        }}
                                                        aria-label="채팅방 이름 수정"
                                                        title="수정"
                                                    >
                                                        <EditIcon size={16} color="var(--ico-color-primary)" />
                                                    </button>
                                                    <button
                                                        type="button"
                                                        className={`${styles['action-button']} ${styles['delete-button']}`}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleDeleteRoomClick(room);
                                                        }}
                                                        aria-label="채팅방 삭제"
                                                        title="삭제"
                                                    >
                                                        <DeleteIcon size={16} color="#ef4444" />
                                                    </button>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </li>
                        )}

                        {/* 비회원 안내 메시지 */}
                        {!isLoggedIn && (
                            <li className={styles['guest-notice']}>
                                <div className={styles['notice-content']}>
                                    <span className={styles['notice-icon']}>ℹ️</span>
                                    <div className={styles['notice-text']}>
                                        <p className={styles['notice-title']}>비회원 모드</p>
                                        <p className={styles['notice-desc']}>
                                            로그인하시면 대화 내역을 저장하고 관리할 수 있습니다.
                                        </p>
                                    </div>
                                </div>
                            </li>
                        )}

                        {/* 로그아웃 버튼 */}
                        <li>
                            <LogoutBtn />
                        </li>
                    </ul>

                    {/* 사이드바 푸터 */}
                    <ul className={styles['sidebar-footer']}>
                        <li className={styles['footer-item']}>
                            <span className={styles['footer-icon']}>
                                {isDarkMode ? '🌙' : '☀️'}
                            </span>
                            <p className={styles['footer-text']}>다크모드</p>
                            <DarkModeToggle
                                isDarkMode={isDarkMode}
                                onToggle={onToggleDarkMode}
                            />
                        </li>
                    </ul>
                </div>
            </aside>

            {/* 삭제 확인 모달 */}
            <DeleteModal
                isOpen={isDeleteModalOpen}
                onClose={() => {
                    setIsDeleteModalOpen(false);
                    setRoomToDelete(null);
                }}
                onConfirm={handleConfirmDelete}
                title="채팅방 삭제"
                message={`"${roomToDelete?.title || ''}" 채팅방을 삭제하시겠습니까?`}
            />
        </>
    );
}

export default SideBar;