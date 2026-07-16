package com.example.chatbotProject.repository;

import com.example.chatbotProject.model.ChatLog;
import com.example.chatbotProject.model.ChatSession;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatLogRepository extends JpaRepository<ChatLog, Long> {

    // 특정 session_id로 로그 조회
    List<ChatLog> findBySession_SessionId(Long sessionId);

    // 특정 ChatSession 엔티티에 해당하는 모든 로그 삭제
    void deleteBySession(ChatSession session);

}
