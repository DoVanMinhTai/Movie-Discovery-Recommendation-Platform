package nlu.fit.movie_backend;

import nlu.fit.movie_backend.config.ServiceUrlConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.data.elasticsearch.repository.config.EnableElasticsearchRepositories;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

import java.util.TimeZone;

@SpringBootApplication
@EnableJpaRepositories(
        basePackages = "nlu.fit.movie_backend.repository.jpa"
)
@EnableElasticsearchRepositories(
        basePackages = "nlu.fit.movie_backend.repository.elasticsearchrepository"
)
@EnableConfigurationProperties(ServiceUrlConfig.class)
public class MovieBackendApplication {
    static {
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Ho_Chi_Minh"));
    }

    public static void main(String[] args) {
        SpringApplication.run(MovieBackendApplication.class, args);
    }

}
