package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 클라이언트가 채팅을 보낼 때 사용하는 요청 DTO
 */
public class ChatRequestDto {

    private String chat; // 사용자 입력 메시지

    @JsonProperty("session_id") // JSON에서 session_id → Java 필드 sessionId로 매핑
    private Long sessionId;

    public String getChat() {
        return chat;
    }

    public void setChat(String chat) {
        this.chat = chat;
    }

    public Long getSessionId() {
        return sessionId;
    }

    public void setSessionId(Long sessionId) {
        this.sessionId = sessionId;
    }
}
