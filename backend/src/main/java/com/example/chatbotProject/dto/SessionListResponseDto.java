package com.example.chatbotProject.dto;

public class SessionListResponseDto {
    private Long sessionId;
    private String title;

    public SessionListResponseDto(Long sessionId, String title) {
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
