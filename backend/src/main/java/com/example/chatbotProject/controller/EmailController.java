package com.example.chatbotProject.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/email")
public class EmailController {

    private final JavaMailSender mailSender;
    // 메모리에 인증코드 저장
    private final Map<String, String> verificationCodes = new ConcurrentHashMap<>();

    public EmailController(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    @PostMapping("/send")
    public ResponseEntity<Map<String, String>> sendVerificationCode(@RequestBody Map<String, String> request) {
        String email = request != null ? request.get("email") : null;

        if (email == null || email.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(mapOf("fail"));
        }

        // 4자리 인증코드
        String code = String.format("%04d", new Random().nextInt(10000));
        verificationCodes.put(email, code);

        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(email);
            message.setSubject("이메일 인증 코드");
            message.setText("인증 코드: " + code);
            mailSender.send(message);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(mapOf("fail"));
        }

        return ResponseEntity.ok(mapOf("success"));
    }

    @PostMapping("/verify")
    public ResponseEntity<Map<String, String>> verifyCode(@RequestBody Map<String, String> request) {
        String email = request != null ? request.get("email") : null;
        String code  = request != null ? request.get("code")  : null;

        if (email == null || email.trim().isEmpty() || code == null || code.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(mapOf("fail"));
        }

        String storedCode = verificationCodes.get(email);
        if (storedCode != null && storedCode.equals(code)) {
            verificationCodes.remove(email); // 재사용 방지
            return ResponseEntity.ok(mapOf("success"));
        } else {
            return ResponseEntity.badRequest().body(mapOf("fail"));
        }
    }

    private Map<String, String> mapOf(String status) {
        Map<String, String> m = new HashMap<>();
        m.put("status", status);
        return m;
    }
}
