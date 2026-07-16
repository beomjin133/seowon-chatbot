package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class LoginRequestDto {

    private String email;

    @JsonProperty("user_password")
    private String userPassword;

    public LoginRequestDto() {}

    // Getters & Setters
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getUserPassword() {
        return userPassword;
    }

    public void setUserPassword(String userPassword) {
        this.userPassword = userPassword;
    }
}
