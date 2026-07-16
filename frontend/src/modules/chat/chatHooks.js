import { useState, useEffect, useRef, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage, addUserMessage, addRoom } from '@/modules/chat/slices/chatSlice';
import { chatRoomCreateApi } from '@/modules/chat/chatApi';

// 비회원 전용 특수 roomId (chatSlice와 동일해야 함)
const GUEST_ROOM_ID = 'guest-session';

// 채팅 기능을 관리하는 커스텀 훅
export const useChat = () => {
    const dispatch = useDispatch();
    const chatEndRef = useRef(null);
    const isCreatingRoom = useRef(false); // 중복 방지

    const selectedRoomId = useSelector((state) => state.chat.selectedRoomId);
    const allMessages = useSelector((state) => state.chat.messages);
    const loading = useSelector((state) => state.chat.loading);
    const error = useSelector((state) => state.chat.error);

    // 로그인 상태 확인
    const token = localStorage.getItem('token');
    const isLoggedIn = !!token;

    const chatList = useMemo(() => {
        // 비회원: GUEST_ROOM_ID의 메시지 표시
        // 회원: selectedRoomId의 메시지 표시 (null이면 빈 배열)
        if (!isLoggedIn) {
            return allMessages[GUEST_ROOM_ID] || [];
        }

        if (!selectedRoomId) {
            return [];
        }

        return allMessages[selectedRoomId] || [];
    }, [allMessages, selectedRoomId, isLoggedIn]);

    const handleSendMessage = async (message) => {
        console.log('=== handleSendMessage 호출 ===');
        console.log('메시지:', message);
        console.log('isLoggedIn:', isLoggedIn);
        console.log('selectedRoomId:', selectedRoomId);
        console.log('isCreatingRoom.current:', isCreatingRoom.current);

        if (!message.trim()) return;

        // 케이스 1: 비회원 - GUEST_ROOM_ID 사용
        if (!isLoggedIn) {
            console.log('케이스 1: 비회원');
            dispatch(addUserMessage(message));
            dispatch(sendMessage(message));
            return;
        }

        // 케이스 2: 회원 + 채팅방 선택됨 - 일반적인 메시지 전송
        if (selectedRoomId) {
            console.log('케이스 2: 회원 + 채팅방 선택됨');
            dispatch(addUserMessage(message));
            dispatch(sendMessage(message));
            return;
        }

        // 케이스 3: 회원 + 채팅방 미선택 (빈 페이지) - 자동으로 "새 채팅" 방 생성 후 메시지 전송
        console.log('케이스 3: 회원 + 채팅방 미선택');

        // 이미 방 생성 중이면 리턴
        if (isCreatingRoom.current) {
            console.log('⚠️ 이미 채팅방 생성 중입니다. 중복 호출 방지');
            return;
        }

        try {
            isCreatingRoom.current = true;
            console.log('🔄 채팅방 생성 시작...');

            // 새 채팅방 생성 (제목: "새 채팅")
            const newRoom = await chatRoomCreateApi('새 채팅');
            console.log('✅ 채팅방 생성 완료:', newRoom);

            const roomId = String(newRoom.id);
            const roomTitle = newRoom.title || '새 채팅';

            // Redux에 새 방 추가 및 선택
            console.log('📝 addRoom dispatch:', { id: roomId, title: roomTitle });
            dispatch(addRoom({ id: roomId, title: roomTitle }));

            // 방 생성 완료 후 메시지 전송
            console.log('💬 메시지 전송 시작');
            dispatch(addUserMessage(message));
            dispatch(sendMessage(message));
            console.log('✅ 메시지 전송 완료');

        } catch (error) {
            console.error('❌ 채팅방 생성 실패:', error);
            alert('채팅방 생성에 실패했습니다. 다시 시도해주세요.');
        } finally {
            isCreatingRoom.current = false;
            console.log('=== handleSendMessage 종료 ===');
        }
    };

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [chatList]);

    return {
        chatList,
        loading,
        error,
        handleSendMessage,
        chatEndRef,
        isLoggedIn,
        selectedRoomId,
    };
};

// 모바일 화면 여부를 감지하는 커스텀 훅
export const useIsMobile = (breakpoint = 768) => {
    const [isMobile, setIsMobile] = useState(
        typeof window !== 'undefined' ? window.innerWidth <= breakpoint : false
    );

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= breakpoint);
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [breakpoint]);

    return isMobile;
};