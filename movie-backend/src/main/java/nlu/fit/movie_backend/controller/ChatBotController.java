package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.ChatbotService;
import nlu.fit.movie_backend.viewmodel.chatbot.ChatPostVm;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/chatbot")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class ChatBotController {
    private final ChatbotService chatbotService;

    @PostMapping(value = "/message", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> sendMessage(@RequestBody ChatPostVm chatPostVm) {
        return Flux.defer(() -> {
            try {
                String jsonResponse = chatbotService.sendMessage(chatPostVm);

                return Flux.just(ServerSentEvent.<String>builder()
                        .data(jsonResponse)
                        .build());
            } catch (Exception e) {
                return Flux.error(e);
            }
        }).onErrorResume(e -> Flux.just(ServerSentEvent.<String>builder()
                .data("{\"error\": \"" + e.getMessage() + "\"}")
                .build()));
    }

    @GetMapping("/history")
    public ResponseEntity<?> getMessages(@RequestParam Long userId) {
        return ResponseEntity.ok(chatbotService.getMessages(userId));
    }
}
