package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.config.ServiceUrlConfig;
import nlu.fit.movie_backend.repository.jpa.MovieRepository;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import nlu.fit.movie_backend.viewmodel.recommendation.MovieSimilarVm;
import nlu.fit.movie_backend.viewmodel.recommendation.UserContext;
import nlu.fit.movie_backend.viewmodel.recommendation.UserFeedResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.data.domain.Limit;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

@Service
@AllArgsConstructor
public class RecommendationService {
    private final ServiceUrlConfig serviceUrlConfig;
    private final RestClient restClient;
    private final MovieRepository movieRepository;

    public String updateRecommendations() {
        final URI url = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/recommendation/reTraining")
                .build().toUri();
        return restClient.post().uri(url)
                .retrieve().body(String.class);
    }

    public List<MovieSimilarVm> getMovieSimilarIdByMovieId(Long movieId) {
        final URI url = UriComponentsBuilder.fromHttpUrl(
                serviceUrlConfig.recommendation()
        ).path("/recommendation/getMovieSimilar/{movieId}")
                .buildAndExpand(movieId).toUri();
        return restClient.get().uri(url).retrieve().body(new ParameterizedTypeReference<List<MovieSimilarVm>>() {});
    }

    public List<MovieThumbnailGetVm> getMovieSimilar(Long movieId) {
        List<Long> ids = getMovieSimilarIdByMovieId(movieId).stream().map(MovieSimilarVm::movieId).toList();
        return movieRepository.findAllByIdIn(ids, Limit.of(10)).stream().map(item -> new MovieThumbnailGetVm(
                item.getId(),item.getTitle(),item.getBackdropPath()
        )).collect(Collectors.toList());
    }

    public UserFeedResponse getPopularMovies(int limit) {
        final URI uri = UriComponentsBuilder.fromHttpUrl(serviceUrlConfig.recommendation())
                .path("/recommendation/popular/{limit}")
                .queryParam("limit", limit)
                .build().toUri();
        return restClient.get().uri(uri).retrieve().body(
                new ParameterizedTypeReference<UserFeedResponse>() {
                });
    }

    public List<UserFeedResponse> getUserFeed(UserContext userContext) {
        final URI url = UriComponentsBuilder.fromHttpUrl(
                serviceUrlConfig.recommendation()
        ).path("/recommendation/getUserFeed").build().toUri();
        return restClient.post().uri(url)
                .body(userContext).retrieve()
                .body(new ParameterizedTypeReference<List<UserFeedResponse>>() {
                });
    }
}
