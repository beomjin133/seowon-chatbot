package com.example.chatbotProject.repository;

import com.example.chatbotProject.model.ChatSession;
import com.example.chatbotProject.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatSessionRepository extends JpaRepository<ChatSession, Long> {
    List<ChatSession> findByUser(User user);
}