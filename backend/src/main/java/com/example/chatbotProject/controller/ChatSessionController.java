package com.example.chatbotProject.controller;

import com.example.chatbotProject.dto.ChatSessionResponseDto;
import com.example.chatbotProject.dto.CreateSessionRequestDto;
import com.example.chatbotProject.dto.UpdateSessionTitleRequestDto;
import com.example.chatbotProject.model.ChatSession;
import com.example.chatbotProject.model.User;
import com.example.chatbotProject.repository.ChatSessionRepository;
import com.example.chatbotProject.repository.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/session")
public class ChatSessionController {

    private final ChatSessionRepository chatSessionRepository;
    private final UserRepository userRepository;

    public ChatSessionController(ChatSessionRepository chatSessionRepository,
                                 UserRepository userRepository) {
        this.chatSessionRepository = chatSessionRepository;
        this.userRepository = userRepository;
    }

    // 세션 생성
    @PostMapping("/create")
    public ResponseEntity<?> createSession(@RequestBody CreateSessionRequestDto requestDto,
                                           Authentication authentication) {
        String userEmail = (String) authentication.getPrincipal();

        Optional<User> userOpt = userRepository.findByEmail(userEmail);
        if (!userOpt.isPresent()) {
            return ResponseEntity.badRequest().body("해당 유저를 찾을 수 없습니다.");
        }

        ChatSession session = new ChatSession();
        session.setUser(userOpt.get());
        session.setTitle(requestDto.getTitle());
        session.setStartedAt(LocalDateTime.now());
        session.setEndedAt(LocalDateTime.now());

        chatSessionRepository.save(session);

        Map<String, Object> response = new HashMap<>();
        response.put("session_id", session.getSessionId());
        response.put("title", requestDto.getTitle());
        return ResponseEntity.ok(response);
    }

    // 세션 타이틀 수정
    @PutMapping("/{session_id}")
    public ResponseEntity<?> updateSessionTitle(@PathVariable("session_id") Long sessionId,
                                                @RequestBody UpdateSessionTitleRequestDto requestDto,
                                                Authentication authentication) {
        String userEmail = (String) authentication.getPrincipal();
        String updatedTitle = requestDto.getUpdateTitle();

        Optional<ChatSession> sessionOpt = chatSessionRepository.findById(sessionId);
        if (!sessionOpt.isPresent()) {
            return ResponseEntity.badRequest().body("해당 세션이 존재하지 않습니다.");
        }

        ChatSession session = sessionOpt.get();
        if (!session.getUser().getEmail().equals(userEmail)) {
            return ResponseEntity.status(403).body("수정 권한이 없습니다.");
        }

        session.setTitle(updatedTitle);
        chatSessionRepository.save(session);

        Map<String, Object> response = new HashMap<>();
        response.put("session_id", session.getSessionId());
        response.put("title", session.getTitle());

        return ResponseEntity.ok(response);
    }

    // 세션 삭제
    @DeleteMapping("/{session_id}")
    public ResponseEntity<?> deleteSession(@PathVariable("session_id") Long sessionId,
                                           Authentication authentication) {
        String userEmail = (String) authentication.getPrincipal();

        Optional<ChatSession> sessionOpt = chatSessionRepository.findById(sessionId);
        if (!sessionOpt.isPresent()) {
            return ResponseEntity.badRequest().body("해당 세션이 존재하지 않습니다.");
        }

        ChatSession session = sessionOpt.get();
        if (!session.getUser().getEmail().equals(userEmail)) {
            return ResponseEntity.status(403).body("삭제 권한이 없습니다.");
        }

        chatSessionRepository.delete(session);

        Map<String, Object> response = new HashMap<>();
        response.put("session_id", sessionId);
        return ResponseEntity.ok(response);
    }

    // 전체 세션 목록 조회
    @PostMapping("/list")
    public ResponseEntity<?> listSessions(Authentication authentication) {
        String userEmail = (String) authentication.getPrincipal();

        Optional<User> userOpt = userRepository.findByEmail(userEmail);
        if (!userOpt.isPresent()) {
            return ResponseEntity.badRequest().body("해당 유저를 찾을 수 없습니다.");
        }

        List<ChatSession> sessions = chatSessionRepository.findByUser(userOpt.get());

        List<Map<String, Object>> result = sessions.stream().map(session -> {
            Map<String, Object> map = new HashMap<>();
            map.put("session_id", session.getSessionId());
            map.put("title", session.getTitle());
            return map;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }

    // 특정 세션의 채팅 로그 조회
    @GetMapping("/{session_id}")
    public ResponseEntity<?> readSessionLogs(@PathVariable("session_id") Long sessionId,
                                             Authentication authentication) {
        String userEmail = (String) authentication.getPrincipal();

        Optional<ChatSession> sessionOpt = chatSessionRepository.findById(sessionId);
        if (!sessionOpt.isPresent()) {
            return ResponseEntity.badRequest().body("해당 세션이 존재하지 않습니다.");
        }

        ChatSession session = sessionOpt.get();
        if (!session.getUser().getEmail().equals(userEmail)) {
            return ResponseEntity.status(403).body("조회 권한이 없습니다.");
        }

        List<Map<String, Object>> logs = session.getChatLogs().stream().map(log -> {
            Map<String, Object> map = new HashMap<>();
            map.put("user_message", log.getUserMessage());
            map.put("bot_response", log.getBotResponse());
            map.put("created_at", log.getCreatedAt().toString());
            return map;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(logs);
    }
}
