package com.example.chatbotProject.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

/**
 * Spring Security 설정 클래스
 * - JWT 기반 인증/인가 처리
 * - 세션 비활성화 (STATELESS)
 * - CORS 및 접근 권한 규칙 정의
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;

    public SecurityConfig(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    /**
     * AuthenticationManager Bean 등록
     * - 로그인 시 Authentication 객체를 만들 때 사용
     */
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    /**
     * CORS 설정
     * - 프론트엔드와의 통신을 위해 허용할 도메인/메서드/헤더 지정
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();

        config.setAllowedOriginPatterns(Arrays.asList("*"));
        config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(Arrays.asList("*"));
        config.setAllowCredentials(true); // 쿠키/인증정보 포함 요청 허용
        config.setMaxAge(3600L); // Pre-flight 요청 캐시 시간(초)

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }

    /**
     * Spring Security 필터 체인 설정
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // CORS 활성화
                .cors().and()
                // CSRF 보호 비활성화 (JWT 기반에서는 불필요)
                .csrf().disable()
                // 세션을 사용하지 않고, 모든 요청은 토큰 기반으로 처리
                .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                // 접근 권한 규칙 설정
                .authorizeRequests()
                .antMatchers(HttpMethod.OPTIONS, "/**").permitAll()   // Pre-flight 요청 허용
                .antMatchers("/api/auth/**").permitAll()             // 회원가입/로그인 허용
                .antMatchers("/api/email/**").permitAll()            // 이메일 인증 허용
                .antMatchers("/api/chat").permitAll()                // 채팅 허용
                .antMatchers("/actuator/**").permitAll()             // 모니터링 엔드포인트 허용
                .anyRequest().authenticated()                        // 나머지는 인증 필요
                .and()
                // 폼 로그인/HTTP Basic 비활성화
                .formLogin().disable()
                .httpBasic().disable();

        // UsernamePasswordAuthenticationFilter 전에 JWT 필터를 실행
        http.addFilterBefore(new JwtAuthenticationFilter(jwtTokenProvider),
                UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
