package nlu.fit.movie_backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "services")
public record ServiceUrlConfig(
        String chatbot, String recommendation, String chatbotToken
) {

}
