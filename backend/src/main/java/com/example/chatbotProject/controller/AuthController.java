package com.example.chatbotProject.controller;

import com.example.chatbotProject.config.JwtTokenProvider;
import com.example.chatbotProject.dto.LoginRequestDto;
import com.example.chatbotProject.dto.RegisterRequestDto;
import com.example.chatbotProject.model.User;
import com.example.chatbotProject.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth/")
public class AuthController {

    private final AuthService authService;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthController(AuthService authService, JwtTokenProvider jwtTokenProvider) {
        this.authService = authService;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequestDto requestDto) {
        User newUser = authService.register(requestDto);
        return ResponseEntity.ok(newUser);
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequestDto requestDto) {
        User user = authService.authenticate(requestDto.getEmail(), requestDto.getUserPassword());
        Map<String, String> response = new HashMap<>();
        if (user != null) {
            String token = jwtTokenProvider.createToken(
                    user.getEmail(),
                    user.getUserName(),
                    user.getProfileImg(),
                    user.getRole()
            );
            response.put("status", "success");
            response.put("token", token);
            response.put("message", "로그인 성공");
            return ResponseEntity.ok(response);
        } else {
            response.put("status", "fail");
            response.put("message", "로그인 실패");
            return ResponseEntity.ok(response);
        }
    }
}
