package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.config.ServiceUrlConfig;
import nlu.fit.movie_backend.repository.jpa.MovieRepository;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import nlu.fit.movie_backend.viewmodel.recommendation.MovieSimilarCBFResponse;
import nlu.fit.movie_backend.viewmodel.recommendation.RecommendationItem;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.data.domain.Limit;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@AllArgsConstructor
public class RecommendationService {
    private final ServiceUrlConfig serviceUrlConfig;
    private final RestClient restClient;
    private final MovieRepository movieRepository;

    public List<MovieThumbnailGetVm> getHybridRecommendations(Long userId, Long movieId, int topN) {
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/api/v1/hybrid/recommendations/{userId}")
                .queryParam("top_n", topN);

        if (movieId != null) {
            builder.queryParam("movie_id", movieId);
        }

        final URI url = builder.buildAndExpand(userId).toUri();

        List<Map<String, Object>> response = restClient.get().uri(url)
                .retrieve().body(new ParameterizedTypeReference<List<Map<String, Object>>>() {
                });

        if (response != null) {
            return response.stream()
                    .map(item -> new MovieThumbnailGetVm(
                            Long.valueOf(item.get("movie_id").toString()),
                            (String) item.get("title"),
                            (String) item.get("poster_path"),
                            null,
                            null
                    )).collect(Collectors.toList());
        }
        return new ArrayList<>();
    }

    public List<MovieThumbnailGetVm> getCollaborativeFiltering(Long userId, int topN) {
        final URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/api/v1/cf/user-recommendations/{userId}")
                .queryParam("top_n", topN)
                .buildAndExpand(userId).toUri();

        List<RecommendationItem> response = restClient.get().uri(url).retrieve().body(new ParameterizedTypeReference<List<RecommendationItem>>() {
        });
        return movieRepository.findAllByIdIn(response.stream().map(item -> item.movie_id()).toList(), Limit.of(10)).stream().map(
                item -> new MovieThumbnailGetVm(item.getId(), item.getTitle(),item.getBackdropPath(),null,null)
        ).toList();
    }

    public List<MovieThumbnailGetVm> getSimilarMoviesCF(Long movieId, int topN) {
        final URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/api/v1/cf/item-similarity/{movieId}")
                .queryParam("top_n", topN)
                .buildAndExpand(movieId).toUri();

        List<Map<String, Object>> response = restClient.get().uri(url)
                .retrieve().body(new ParameterizedTypeReference<List<Map<String, Object>>>() {
                });

        if (response != null) {
            return response.stream()
                    .map(item -> new MovieThumbnailGetVm(
                            Long.valueOf(item.get("movie_id").toString()),
                            (String) item.get("title"),
                            (String) item.get("poster_path"),null,null
                    )).collect(Collectors.toList());
        }
        return new ArrayList<>();
    }

    public List<MovieThumbnailGetVm> searchMoviesCBF(String query, int topN) {
        final URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/api/v1/cbf/search") 
                .queryParam("query", query)
                .queryParam("top_n", topN)
                .build().toUri();

        return restClient.get().uri(url).retrieve().body(new ParameterizedTypeReference<List<MovieThumbnailGetVm>>() {
        });
    }

    public List<MovieThumbnailGetVm> getSimilarMoviesCBF(Long movieId, int topN) {
        final URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/api/v1/cbf/similar/{movieId}")
                .queryParam("top_n", topN)
                .buildAndExpand(movieId).toUri();

        MovieSimilarCBFResponse response = restClient.get().uri(url).retrieve().body(MovieSimilarCBFResponse.class);
        if (response != null && response.recommendations() != null) {
            List<Long> ids = response.recommendations().stream()
                    .map(item -> Long.parseLong(item.movie_id()))
                    .toList();
            return movieRepository.findAllByIdIn(ids, Limit.of(topN)).stream()
                    .map(m -> new MovieThumbnailGetVm(m.getId(), m.getTitle(), m.getBackdropPath(),null,null))
                    .toList();
        }
        return new ArrayList<>();
    }
}
