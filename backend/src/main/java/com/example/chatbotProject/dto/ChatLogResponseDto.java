package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;

public class ChatLogResponseDto {

    @JsonProperty("user_message")
    private String userMessage;

    @JsonProperty("bot_response")
    private String botResponse;

    @JsonProperty("response_time")
    private int responseTime;

    @JsonProperty("created_at")
    private LocalDateTime createdAt;

    // 생성자
    public ChatLogResponseDto(String userMessage, String botResponse, int responseTime, LocalDateTime createdAt) {
        this.userMessage = userMessage;
        this.botResponse = botResponse;
        this.responseTime = responseTime;
        this.createdAt = createdAt;
    }

    // Getter
    public String getUserMessage() { return userMessage; }
    public String getBotResponse() { return botResponse; }
    public int getResponseTime() { return responseTime; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
