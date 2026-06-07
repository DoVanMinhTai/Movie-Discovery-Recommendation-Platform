package nlu.fit.movie_backend.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "es")
@Data
public class OpenSearchProperties {
    private String host;
    private String url;
    private String username;
    private String password;
}
