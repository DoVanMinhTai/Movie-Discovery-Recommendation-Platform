package nlu.fit.movie_backend.config;

import lombok.AllArgsConstructor;
import org.opensearch.client.RestHighLevelClient;
import org.opensearch.data.client.orhlc.ClientConfiguration;
import org.opensearch.data.client.orhlc.RestClients;
import org.springframework.context.annotation.Configuration;

import org.opensearch.data.client.orhlc.AbstractOpenSearchConfiguration;
import org.springframework.data.elasticsearch.repository.config.EnableElasticsearchRepositories;

@Configuration
@AllArgsConstructor
@EnableElasticsearchRepositories(basePackages = "nlu.fit.movie_backend.repository.elasticsearchrepository")
public class OpenSearchConfig extends AbstractOpenSearchConfiguration {
    private final OpenSearchProperties openSearchProperties;

    @Override
    public RestHighLevelClient opensearchClient() {
        final ClientConfiguration clientConfiguration =  ClientConfiguration.builder()
                .connectedTo(openSearchProperties.getHost())
                .usingSsl()
                .withBasicAuth(openSearchProperties.getUsername(), openSearchProperties.getPassword())
                .build();
        return RestClients.create(clientConfiguration).rest();
    }
}