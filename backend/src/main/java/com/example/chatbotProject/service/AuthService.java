package com.example.chatbotProject.service;

import com.example.chatbotProject.dto.RegisterRequestDto;
import com.example.chatbotProject.model.User;
import com.example.chatbotProject.repository.UserRepository;
import org.springframework.security.crypto.bcrypt.BCrypt;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class AuthService {

    private final UserRepository userRepository;

    public AuthService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    // 회원가입
    public User register(RegisterRequestDto requestDto) {
        String hashedPassword = BCrypt.hashpw(requestDto.getUserPassword(), BCrypt.gensalt());

        User user = new User();
        user.setEmail(requestDto.getEmail());
        user.setUserPassword(hashedPassword);
        user.setUserName(requestDto.getUserName());
        user.setProfileImg(requestDto.getProfileImg());
        user.setRole("user");

        return userRepository.save(user);
    }

    // 로그인 인증
    public User authenticate(String email, String rawPassword) {
        Optional<User> userOpt = userRepository.findByEmail(email);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            if (BCrypt.checkpw(rawPassword, user.getUserPassword())) {
                return user;
            }
        }
        return null;
    }
}
