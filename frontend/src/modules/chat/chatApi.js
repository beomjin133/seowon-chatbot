import axios from '../shared/api/axiosInstance';

/**
 * 채팅 메시지 전송 API
 * @param {Object} params
 * @param {string} params.message - 전송할 메시지
 * @param {string|null} params.sessionId - 세션 ID (비회원은 null)
 * @returns {Promise<Object>} - { response: "봇 응답 메시지" }
 */
export const chatApi = async ({ message, sessionId }) => {
    const response = await axios.post('/chat', {
        chat: message,
        session_id: sessionId, // 비회원일 경우 null 또는 undefined
    });
    return response.data; // { message: "..." } 또는 { response: "..." }
};

/**
 * 채팅방 생성 API
 * @param {string} title - 채팅방 제목
 * @returns {Promise<Object>} - { id: number, title: string }
 */
export const chatRoomCreateApi = async (title) => {
    const response = await axios.post('/session/create', { title });
    return {
        id: response.data.session_id,
        title: response.data.title,
    };
};

/**
 * 채팅방 목록 조회 API
 * @returns {Promise<Array>} - [{ session_id, title, ended_at }]
 */
export const chatRoomListApi = async () => {
    const response = await axios.post('/session/list');
    return response.data; // [{ session_id, title, ended_at }]
};

/**
 * 채팅 히스토리 조회 API
 * @param {string} sessionId - 세션 ID
 * @returns {Promise<Array>} - [{ user_message, bot_response, created_at }]
 */
export const chatHistoryApi = async (sessionId) => {
    const response = await axios.get(`/session/${sessionId}`);
    return response.data; // [{ user_message, bot_response, created_at }]
};

/**
 * 채팅방 삭제 API
 * @param {string} sessionId - 세션 ID
 * @returns {Promise<Object>}
 */
export const chatRoomDeleteApi = async (sessionId) => {
    const response = await axios.delete(`/session/${sessionId}`);
    return response.data;
};

/**
 * 채팅방 제목 수정 API
 * @param {string} sessionId - 세션 ID
 * @param {string} newTitle - 새 제목
 * @returns {Promise<Object>}
 */
export const chatRoomUpdateApi = async (sessionId, newTitle) => {
    const response = await axios.put(`/session/${sessionId}`, {
        update_title: newTitle,
    });
    return response.data;
};