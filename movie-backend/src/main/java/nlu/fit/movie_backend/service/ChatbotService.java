package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.config.ServiceUrlConfig;

import nlu.fit.movie_backend.viewmodel.chatbot.ChatPostVm;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.util.UriComponentsBuilder;
import reactor.core.publisher.Flux;

import java.net.URI;
import java.util.List;

@Service
@AllArgsConstructor
public class ChatbotService {
    private final ServiceUrlConfig serviceUrlConfig;
    private final WebClient webClient;
    private final RestClient restClient;

    public Flux<String> sendMessage(ChatPostVm chatRequest) {
        URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.chatbot())
                .path("/chatbot/sendMessage")
                .build().toUri();

        return webClient.post().uri(url).bodyValue(chatRequest)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class)
                .map(data -> data)
                .filter(data -> !data.isBlank())
                ;
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
