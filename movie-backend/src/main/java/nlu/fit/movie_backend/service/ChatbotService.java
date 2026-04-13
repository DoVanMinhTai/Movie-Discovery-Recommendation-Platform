package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.config.ServiceUrlConfig;

import nlu.fit.movie_backend.viewmodel.chatbot.ChatPostVm;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;

@Service
@AllArgsConstructor
public class ChatbotService {
    private final ServiceUrlConfig serviceUrlConfig;
    private final RestClient restClient;

    public String sendMessage(ChatPostVm chatRequest) {
        try {
            return restClient.post()
                    .uri(serviceUrlConfig.chatbot() + "/chatbot/sendMessage")
                    .header("Authorization", "Bearer " + serviceUrlConfig.chatbotToken())
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                    .header("Accept", "application/json")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(chatRequest)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        System.err.println("Mã lỗi: " + response.getStatusCode());
                    })
                    .body(String.class);
        } catch (Exception e) {
            return "{\"error\": \"Không thể kết nối đến Hugging Face: " + e.getMessage() + "\"}";
        }
    }

    public Object getMessages(Long userId) {
        URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.chatbot())
                .path("/chatbot/getMessage")
                .queryParam("userId", userId)
                .build().toUri();
        return restClient.get().uri(url).retrieve()
                .body(Object.class);
    }
}
