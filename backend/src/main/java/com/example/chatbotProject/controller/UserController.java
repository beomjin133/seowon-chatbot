package com.example.chatbotProject.controller;

import com.example.chatbotProject.dto.PasswordChangeRequestDto;
import com.example.chatbotProject.dto.UserUpdateRequestDto;
import com.example.chatbotProject.model.User;
import com.example.chatbotProject.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
        this.passwordEncoder = new BCryptPasswordEncoder(); // 직접 주입하거나 @Bean으로 설정 가능
    }

    @PutMapping("/{email}")
    public ResponseEntity<?> updateUserInfo(@PathVariable String email,
                                            @RequestBody UserUpdateRequestDto request,
                                            Authentication authentication) {
        String tokenEmail = (String) authentication.getPrincipal();

        if (!tokenEmail.equals(email)) {
            Map<String, String> response = new HashMap<>();
            response.put("status", "fail");
            response.put("message", "본인만 수정할 수 있습니다.");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(response);
        }

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다."));

        user.setUserName(request.getNew_name());
        user.setProfileImg(request.getProfile_img_url());
        userRepository.save(user);

        Map<String, String> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "회원정보가 성공적으로 변경되었습니다.");
        response.put("new_profile_img", request.getProfile_img_url());
        response.put("new_name", request.getNew_name());

        return ResponseEntity.ok(response);
    }

    @PutMapping("/password")
    public ResponseEntity<?> changePassword(@RequestBody PasswordChangeRequestDto request,
                                            Authentication authentication) {
        String email = (String) authentication.getPrincipal();

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다."));

        if (!passwordEncoder.matches(request.getCurrent_password(), user.getUserPassword())) {
            Map<String, String> response = new HashMap<>();
            response.put("status", "fail");
            response.put("message", "현재 비밀번호가 일치하지 않습니다.");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
        }

        user.setUserPassword(passwordEncoder.encode(request.getNew_password()));
        userRepository.save(user);

        Map<String, String> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "비밀번호가 성공적으로 변경되었습니다.");
        return ResponseEntity.ok(response);
    }
}
