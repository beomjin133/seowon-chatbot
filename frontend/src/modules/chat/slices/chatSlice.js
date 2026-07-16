import { createSlice, createAsyncThunk, current } from '@reduxjs/toolkit';
import {
    chatApi,
    chatRoomListApi,
    chatHistoryApi,
    chatRoomDeleteApi,
    chatRoomUpdateApi,
} from '@/modules/chat/chatApi';
import { saveChatState } from '@/modules/shared/utils/localStorage';

// 비회원 전용 특수 roomId
const GUEST_ROOM_ID = 'guest-session';

export const fetchRoomList = createAsyncThunk(
    'chat/fetchRoomList',
    async () => {
        const rooms = await chatRoomListApi();
        return rooms || [];
    }
);

export const fetchChatHistory = createAsyncThunk(
    'chat/fetchChatHistory',
    async (sessionId) => {
        const history = await chatHistoryApi(sessionId);
        return { sessionId, history };
    }
);

export const sendMessage = createAsyncThunk(
    'chat/sendMessage',
    async (message, { getState, rejectWithValue }) => {
        try {
            const state = getState();
            const sessionId = state.chat.selectedRoomId;
            const response = await chatApi({ message, sessionId });
            return { response };
        } catch (error) {
            return rejectWithValue('메시지 전송 실패');
        }
    }
);

export const deleteChatRoom = createAsyncThunk(
    'chat/deleteRoom',
    async (sessionId) => {
        await chatRoomDeleteApi(sessionId);
        return sessionId;
    }
);

export const updateChatRoomTitle = createAsyncThunk(
    'chat/updateRoomTitle',
    async ({ sessionId, newTitle }) => {
        await chatRoomUpdateApi(sessionId, newTitle);
        return { sessionId, newTitle };
    }
);

const initialState = {
    selectedRoomId: null,
    rooms: [],
    messages: {},
    loading: false,
    error: null,
};

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        selectRoom: (state, action) => {
            const roomId = action.payload;
            state.selectedRoomId = roomId;
            // 빈 배열로 시작
            if (!state.messages[roomId]) {
                state.messages[roomId] = [];
            }
        },
        // 새 채팅 시작 (빈 채팅방으로 이동)
        startNewChat: (state) => {
            state.selectedRoomId = null;
            // 메시지는 초기화하지 않고, selectedRoomId만 null로 설정
        },
        addUserMessage: (state, action) => {
            // 비회원: GUEST_ROOM_ID 사용
            // 회원: selectedRoomId 사용
            const roomId = state.selectedRoomId || GUEST_ROOM_ID;

            if (!state.messages[roomId]) {
                state.messages[roomId] = [];
            }
            state.messages[roomId].push({ type: 'user', text: action.payload });

            // 비회원이 아닐 때만 localStorage 저장
            if (state.selectedRoomId) {
                saveChatState(current(state));
            }
        },
        addRoom: (state, action) => {
            const { id, title } = action.payload;
            if (!state.rooms.find((room) => room.id === id)) {
                state.rooms.push({ id, title });
            }
            // 빈 배열로 시작
            if (!state.messages[id]) {
                state.messages[id] = [];
            }
            state.selectedRoomId = id;
            saveChatState(current(state));
        },
        // 비회원용 게스트 세션 초기화
        initGuestSession: (state) => {
            state.selectedRoomId = null;
            if (!state.messages[GUEST_ROOM_ID]) {
                state.messages[GUEST_ROOM_ID] = [];
            }
        },
        // 비회원 채팅 초기화
        clearGuestChat: (state) => {
            delete state.messages[GUEST_ROOM_ID];
            if (state.selectedRoomId === GUEST_ROOM_ID) {
                state.selectedRoomId = null;
            }
        },
        resetChat: (state) => {
            Object.assign(state, initialState);
            saveChatState(initialState);
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(sendMessage.pending, (state) => {
                state.loading = true;
                state.error = null;

                // 로딩 메시지 추가
                const roomId = state.selectedRoomId || GUEST_ROOM_ID;
                if (!state.messages[roomId]) {
                    state.messages[roomId] = [];
                }
                state.messages[roomId].push({
                    type: 'loading',
                    text: '응답 생성 중...',
                });
            })
            .addCase(sendMessage.fulfilled, (state, action) => {
                state.loading = false;
                const roomId = state.selectedRoomId || GUEST_ROOM_ID;

                if (!state.messages[roomId]) {
                    state.messages[roomId] = [];
                }

                // 로딩 메시지 제거
                state.messages[roomId] = state.messages[roomId].filter(
                    (msg) => msg.type !== 'loading'
                );

                // 봇 응답 추가
                state.messages[roomId].push({
                    type: 'bot',
                    text: action.payload.response.message ||
                        action.payload.response.response ||
                        action.payload.response,
                });

                // 비회원이 아닐 때만 localStorage 저장
                if (state.selectedRoomId) {
                    saveChatState(current(state));
                }
            })
            .addCase(sendMessage.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;

                // 로딩 메시지 제거
                const roomId = state.selectedRoomId || GUEST_ROOM_ID;
                if (state.messages[roomId]) {
                    state.messages[roomId] = state.messages[roomId].filter(
                        (msg) => msg.type !== 'loading'
                    );

                    // 에러 메시지 추가
                    state.messages[roomId].push({
                        type: 'error',
                        text: '죄송합니다. 응답을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요.',
                    });
                }
            })
            .addCase(fetchRoomList.fulfilled, (state, action) => {
                const fetchedRooms = action.payload || [];
                const newRooms = [];
                fetchedRooms.forEach((room) => {
                    const id = String(room.session_id);
                    const title = room.title;
                    newRooms.push({ id, title, endedAt: room.ended_at });
                    // 빈 배열로 시작
                    if (!state.messages[id]) {
                        state.messages[id] = [];
                    }
                });
                state.rooms = newRooms;
                saveChatState(current(state));
            })
            .addCase(fetchChatHistory.fulfilled, (state, action) => {
                const { sessionId, history } = action.payload;
                state.messages[sessionId] = [];
                history.forEach((item) => {
                    state.messages[sessionId].push({
                        type: 'user',
                        text: item.user_message,
                    });
                    state.messages[sessionId].push({
                        type: 'bot',
                        text: item.bot_response,
                    });
                });
                saveChatState(current(state));
            })
            .addCase(deleteChatRoom.fulfilled, (state, action) => {
                const sessionId = String(action.payload);
                state.rooms = state.rooms.filter((room) => room.id !== sessionId);
                delete state.messages[sessionId];
                if (state.selectedRoomId === sessionId) {
                    state.selectedRoomId = null;
                }
                saveChatState(current(state));
            })
            .addCase(updateChatRoomTitle.fulfilled, (state, action) => {
                const { sessionId, newTitle } = action.payload;
                const room = state.rooms.find((r) => r.id === sessionId);
                if (room) {
                    room.title = newTitle;
                }
                saveChatState(current(state));
            });
    },
});

export const {
    selectRoom,
    startNewChat,
    addUserMessage,
    addRoom,
    initGuestSession,
    clearGuestChat,
    resetChat
} = chatSlice.actions;

export default chatSlice.reducer;