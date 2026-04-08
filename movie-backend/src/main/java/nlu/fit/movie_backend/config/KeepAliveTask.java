package nlu.fit.movie_backend.config;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class KeepAliveTask {
    @Scheduled(fixedRate = 600000)
    public void keepAlive() {
        try {
            RestTemplate restTemplate = new RestTemplate();
            String url = "https://movie-discovery-recommendation-platform.onrender.com/actuator/health";
            restTemplate.getForObject(url, String.class);
            System.out.println("Self-ping sent to keep server awake.");
        } catch (Exception e) {
            System.err.println("Self-ping failed: " + e.getMessage());
        }
    }
}
