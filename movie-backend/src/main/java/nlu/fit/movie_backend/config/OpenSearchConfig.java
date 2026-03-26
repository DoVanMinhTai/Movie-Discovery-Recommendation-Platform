package nlu.fit.movie_backend.config;

import org.opensearch.client.RestHighLevelClient;
import org.opensearch.data.client.orhlc.ClientConfiguration;
import org.opensearch.data.client.orhlc.RestClients;
import org.springframework.context.annotation.Configuration;

import org.opensearch.data.client.orhlc.AbstractOpenSearchConfiguration;

@Configuration
public class OpenSearchConfig extends AbstractOpenSearchConfiguration {

    @Override
    public RestHighLevelClient opensearchClient() {
        final ClientConfiguration clientConfiguration =  ClientConfiguration.builder()
                .connectedTo("movie-elasticsearch-1narwfje.us-east-1.bonsaisearch.net:443")
                .usingSsl()
                .withBasicAuth("4f4693845a", "93cd64cc6ffae49747af")
                .build();
        return RestClients.create(clientConfiguration).rest();
    }
}