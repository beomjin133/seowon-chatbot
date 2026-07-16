package com.example.chatbotProject.model;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_logs")
public class ChatLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // session_id: FK
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private ChatSession session;

    @Column(name = "user_message", columnDefinition = "TEXT")
    private String userMessage;

    @Column(name = "bot_response", columnDefinition = "TEXT")
    private String botResponse;

    @Column(name = "response_time")
    private int responseTime;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    // Getters & Setters
    public Long getId() { return id; }

    public ChatSession getSession() { return session; }
    public void setSession(ChatSession session) { this.session = session; }

    public String getUserMessage() { return userMessage; }
    public void setUserMessage(String userMessage) { this.userMessage = userMessage; }

    public String getBotResponse() { return botResponse; }
    public void setBotResponse(String botResponse) { this.botResponse = botResponse; }

    public int getResponseTime() { return responseTime; }
    public void setResponseTime(int responseTime) { this.responseTime = responseTime; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
