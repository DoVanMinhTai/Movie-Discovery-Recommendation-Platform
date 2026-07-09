package nlu.fit.movie_backend.config;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
    name = "keepalive.enabled", havingValue = "true", matchIfMissing = false)
public class KeepAliveTask {
    
    private final RestTemplate restTemplate = new RestTemplate();

    @Scheduled(fixedRate = 600000, initialDelay = 60000)
    public void keepAlive() {
        try {
            String url = "https://<YOUR-HF-SPACE>.hf.space/actuator/health";
            restTemplate.getForObject(url, String.class);
            System.out.println("Self-ping sent to keep server awake.");
        } catch (Exception e) {
            System.err.println("Self-ping failed: " + e.getMessage());
        }
    }
}
