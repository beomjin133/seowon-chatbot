// src/modules/shared/utils/localStorage.js

export const saveChatState = (chatState) => {
    try {
      localStorage.setItem("chatState", JSON.stringify(chatState));
    } catch (err) {
      console.error("❌ 채팅 상태 저장 실패:", err);
    }
  };
  
  export const loadChatState = () => {
    try {
      const saved = localStorage.getItem("chatState");
      return saved ? JSON.parse(saved) : undefined;
    } catch (err) {
      console.error("❌ 채팅 상태 불러오기 실패:", err);
      return undefined;
    }
  };

export const clearAllLocalStorage = () => {
  try {
    console.log("로컬스토리지 초기화 시도 중...");
    localStorage.removeItem("token");
    localStorage.removeItem("chatState");
    console.log("✅ 로컬스토리지 초기화 완료");
  } catch (err) {
    console.error("❌ 로컬스토리지 초기화 실패:", err);
  }
};