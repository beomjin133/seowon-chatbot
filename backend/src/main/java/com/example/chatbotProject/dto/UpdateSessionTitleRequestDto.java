package com.example.chatbotProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class UpdateSessionTitleRequestDto {

    @JsonProperty("update_title")
    private String updateTitle;

    public String getUpdateTitle() {
        return updateTitle;
    }

    public void setUpdateTitle(String updateTitle) {
        this.updateTitle = updateTitle;
    }
}