// src/modules/chat/chatStore.js
import chatReducer from '@/modules/chat/slices/chatSlice';
import { loadChatState } from '@/modules/shared/utils/localStorage';

const persistedState = loadChatState();

const chatReducers = {
  chat: (state = persistedState || undefined, action) =>
    chatReducer(state, action),
};

export default chatReducers;
