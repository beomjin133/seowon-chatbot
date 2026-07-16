// com.example.chatbotProject.dto.ChatSessionResponseDto.java

package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 채팅 세션 정보를 응답할 때 사용하는 DTO
 */
public class ChatSessionResponseDto {

    @JsonProperty("session_id") // JSON 응답에서 session_id로 표시
    private Long sessionId;

    private String title;

    public ChatSessionResponseDto(Long sessionId, String title) {
        this.sessionId = sessionId;
        this.title = title;
    }

    public Long getSessionId() {
        return sessionId;
    }

    public void setSessionId(Long sessionId) {
        this.sessionId = sessionId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }
}
