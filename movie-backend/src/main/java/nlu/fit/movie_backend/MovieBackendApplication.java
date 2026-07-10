package nlu.fit.movie_backend;

import nlu.fit.movie_backend.config.ServiceUrlConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.data.elasticsearch.repository.config.EnableElasticsearchRepositories;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;

import java.util.TimeZone;

@SpringBootApplication
@EnableConfigurationProperties(ServiceUrlConfig.class)
@EnableJpaAuditing
@EnableScheduling
@EnableJpaRepositories(basePackages = "nlu.fit.movie_backend.repository.jpa")
@EnableElasticsearchRepositories(basePackages = "nlu.fit.movie_backend.repository.elasticsearchrepository")
public class MovieBackendApplication {
    static {
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Ho_Chi_Minh"));
    }
    
    public static void main(String[] args) {
        String envMode = System.getenv("ENV") != null ? System.getenv("ENV") : "dev";
        String envFileName = ".env." + envMode;
        
        io.github.cdimascio.dotenv.Dotenv dotenv = io.github.cdimascio.dotenv.Dotenv.configure()
                .directory("../")
                .filename(envFileName)
                .ignoreIfMissing()
                .load();

        System.out.println("Loaded environment from: ../" + envFileName);
        dotenv.entries().forEach(entry -> System.setProperty(entry.getKey(), entry.getValue()));

        SpringApplication.run(MovieBackendApplication.class, args);
    }

}
