package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.config.ServiceUrlConfig;

import nlu.fit.movie_backend.constants.ErrorCode;
import nlu.fit.movie_backend.exception.AppException;
import nlu.fit.movie_backend.viewmodel.chatbot.ChatPostVm;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;

@Service
@AllArgsConstructor
public class ChatbotService {
    private final ServiceUrlConfig serviceUrlConfig;
    private final RestClient restClient;

    public Object sendMessage(ChatPostVm chatRequest) {

        try {
            return restClient.post()
                    .uri(serviceUrlConfig.chatbot() + "/chatbot/sendMessage")
                    .header("Authorization", "Bearer " + serviceUrlConfig.hfToken())
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                    .header("Accept", "application/json")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(chatRequest)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {

                        HttpStatusCode httpStatus = response.getStatusCode();

                        if (httpStatus.equals(HttpStatus.BAD_REQUEST)) {
                            throw new AppException(ErrorCode.INVALID_CHAT_REQUEST);
                        } else if (httpStatus.equals(HttpStatus.TOO_MANY_REQUESTS)) {
                            throw new AppException(ErrorCode.MAX_CHAT_LIMIT_REACHED);
                        } else {
                            throw new AppException(ErrorCode.CHATBOT_SERVICE_UNAVAILABLE);
                        }
                    })
                    .body(Object.class);
        } catch (ResourceAccessException e) {
            throw new AppException(ErrorCode.CHATBOT_SERVICE_UNAVAILABLE);
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
