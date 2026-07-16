import { configureStore } from "@reduxjs/toolkit";
import authReducers from "@/modules/auth/authStore";
import chatReducers from "@/modules/chat/chatStore";
import { loadChatState } from "@/modules/shared/utils/localStorage"; // ✅ 추가

const store = configureStore({
  reducer: {
    ...authReducers,
    ...chatReducers,
  },
  preloadedState: {
    chat: loadChatState(), // ✅ chat 상태만 로컬스토리지에서 불러오기
  },
  devTools: process.env.NODE_ENV !== "production",
});

export default store;