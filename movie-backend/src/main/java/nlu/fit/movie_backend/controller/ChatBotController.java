package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.service.ChatbotService;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.chatbot.ChatPostVm;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class ChatBotController {
    private final ChatbotService chatbotService;
    private final JWTService jWTService;

    @PostMapping(ApiEndpoints.Chatbot.CHATBOT)
    public ResponseEntity<ApiResponse<Object>> sendMessage(@RequestHeader("Authorization") String authHeader, @RequestBody ChatPostVm chatPostVm) {
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);

        ChatPostVm updatedChatPostVm = new ChatPostVm(
                userId,
                chatPostVm.message(),
                chatPostVm.historyMessageList()
        );

        return ResponseEntity.ok(ApiResponse.<Object>builder()
                .result(chatbotService.sendMessage(updatedChatPostVm))
                .build());
    }

    @GetMapping(ApiEndpoints.Chatbot.HISTORY)
    public ResponseEntity<?> getMessages(@RequestParam Long userId) {
        return ResponseEntity.ok(chatbotService.getMessages(userId));
    }
}
