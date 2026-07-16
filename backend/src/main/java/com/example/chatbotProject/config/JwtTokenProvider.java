package com.example.chatbotProject.config;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;

import org.springframework.security.core.Authentication;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.GrantedAuthority;

import java.util.Collections;
import java.util.List;

/**
 * JWT 토큰 생성, 검증, 클레임 추출을 담당하는 클래스
 */
@Component
public class JwtTokenProvider {

    private final Key key;                      // JWT 서명에 사용할 비밀 키
    private final long validityInMilliseconds;  // 토큰 유효 시간(ms 단위)

    /**
     * secret과 유효 시간을 application.yml(application.properties)에서 주입받아 초기화
     */
    public JwtTokenProvider(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.token-validity-in-seconds}") long validityInSeconds
    ) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes());
        this.validityInMilliseconds = validityInSeconds * 1000;
    }

    /**
     * JWT 토큰 생성
     * @param userId 사용자 ID
     * @param userName 사용자 이름
     * @param userProfile 프로필 이미지 URL
     * @param role 사용자 권한(Role)
     * @return 생성된 JWT 토큰 문자열
     */
    public String createToken(String userId, String userName, String userProfile, String role) {
        long now = System.currentTimeMillis();
        Date issuedAt = new Date(now);                       // 발급 시각
        Date validity = new Date(now + validityInMilliseconds); // 만료 시각

        return Jwts.builder()
                .setSubject(userId)                          // sub: 사용자 ID
                .setIssuer("chatbot.api")                    // iss: 발급자
                .setAudience("client")                       // aud: 대상
                .claim("user_name", userName)                // 사용자 이름
                .claim("user_profile", userProfile)          // 프로필 이미지
                .claim("role", role)                         // 권한 정보
                .setIssuedAt(issuedAt)                       // iat: 발급 시간
                .setExpiration(validity)                     // exp: 만료 시간
                .signWith(key, SignatureAlgorithm.HS256)     // HMAC-SHA256 서명
                .compact();
    }

    /**
     * 토큰 유효성 검증
     * @param token JWT 토큰
     * @return 유효하면 true, 유효하지 않으면 false
     */
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(key)
                    .build()
                    .parseClaimsJws(token); // 파싱 과정에서 예외가 발생하면 잘못된 토큰
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * 토큰에서 userId(subject) 추출
     */
    public String getUserIdFromToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }

    /**
     * 토큰에서 모든 클레임 추출
     */
    public Claims getAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    /**
     * 토큰에서 Authentication 객체 생성
     * - userId(subject)를 Principal로 사용
     * - role 정보를 GrantedAuthority로 변환
     */
    public Authentication getAuthentication(String token) {
        Claims claims = getAllClaims(token);

        String userId = claims.getSubject();
        String role = claims.get("role", String.class);

        List<GrantedAuthority> authorities =
                Collections.singletonList(new SimpleGrantedAuthority(role));

        return new UsernamePasswordAuthenticationToken(userId, "", authorities);
    }
}
