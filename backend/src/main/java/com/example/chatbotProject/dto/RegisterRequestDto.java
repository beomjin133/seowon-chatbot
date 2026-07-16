package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class RegisterRequestDto {
    private String email;

    @JsonProperty("user_password")
    private String userPassword;

    @JsonProperty("user_name")
    private String userName;



    @JsonProperty("profile_img")
    private String profileImg;

    public RegisterRequestDto() {}

    // Getters & Setters
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getUserPassword() { return userPassword; }
    public void setUserPassword(String userPassword) { this.userPassword = userPassword; }

    public String getUserName() { return userName; }
    public void setUserName(String userName) { this.userName = userName; }

    public String getProfileImg() { return profileImg; }
    public void setProfileImg(String profileImg) { this.profileImg = profileImg; }
}
