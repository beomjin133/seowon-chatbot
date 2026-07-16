package com.example.chatbotProject.controller;

import com.example.chatbotProject.dto.ChatRequestDto;
import com.example.chatbotProject.model.ChatLog;
import com.example.chatbotProject.model.ChatSession;
import com.example.chatbotProject.repository.ChatLogRepository;
import com.example.chatbotProject.repository.ChatSessionRepository;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class ChatController {

    private final ChatLogRepository chatLogRepository;
    private final ChatSessionRepository chatSessionRepository;

    // 외부 API URL (환경변수로 관리해도 좋음)
    private static final String EXTERNAL_CHAT_URL = "http://123.111.17.25:8000/chat";

    public ChatController(ChatLogRepository chatLogRepository,
                          ChatSessionRepository chatSessionRepository) {
        this.chatLogRepository = chatLogRepository;
        this.chatSessionRepository = chatSessionRepository;
    }

    @PostMapping("/chat")
    public ResponseEntity<?> chat(@RequestBody ChatRequestDto requestDto,
                                  @RequestHeader(value = "Authorization", required = false) String token,
                                  Authentication authentication) {

        String userInput = requestDto.getChat();
        LocalDateTime startTime = LocalDateTime.now();
        long start = System.currentTimeMillis();

        // ---- 외부 API 호출 ----
        String pythonOutput = callExternalChatApi(userInput);
        long duration = System.currentTimeMillis() - start;

        System.out.println("User Message: " + userInput);
        System.out.println("Bot Response: " + pythonOutput);

        Long sessionId = requestDto.getSessionId();
        if (authentication == null || sessionId == null || sessionId == 0L) {
            System.out.println("비회원 채팅입니다 " + sessionId);
            Map<String, Object> response = new HashMap<>();
            response.put("message", pythonOutput);
            response.put("responseTime", duration);
            response.put("timestamp", startTime);
            return ResponseEntity.ok(response);
        }

        ChatSession session = chatSessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("해당 세션 없음"));

        ChatLog log = new ChatLog();
        log.setSession(session);
        log.setUserMessage(userInput);
        log.setBotResponse(pythonOutput);
        log.setResponseTime((int) duration);
        log.setCreatedAt(startTime);
        chatLogRepository.save(log);

        session.setEndedAt(startTime);
        chatSessionRepository.save(session);

        Map<String, Object> response = new HashMap<>();
        response.put("message", pythonOutput);
        response.put("responseTime", duration);
        response.put("timestamp", startTime);
        return ResponseEntity.ok(response);
    }

    /**
     * 외부 RAG 서버에 질문을 전송하고, answer만 추출하는 메서드
     */
    private String callExternalChatApi(String question) {
        try {
            RestTemplate restTemplate = new RestTemplate();

            // 요청 헤더
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // 요청 바디
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("question", question);

            HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(requestBody, headers);

            // POST 요청
            ResponseEntity<Map> responseEntity = restTemplate.exchange(
                    EXTERNAL_CHAT_URL,
                    HttpMethod.POST,
                    requestEntity,
                    Map.class
            );

            // 응답에서 answer 추출
            if (responseEntity.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> body = responseEntity.getBody();
                if (body != null && body.containsKey("answer")) {
                    return body.get("answer").toString();
                } else {
                    return "응답 데이터에 'answer' 필드가 없습니다.";
                }
            } else {
                return "외부 서버 응답 오류: " + responseEntity.getStatusCode();
            }

        } catch (Exception e) {
            e.printStackTrace();
            return "외부 API 호출 중 오류 발생: " + e.getMessage();
        }
    }
}