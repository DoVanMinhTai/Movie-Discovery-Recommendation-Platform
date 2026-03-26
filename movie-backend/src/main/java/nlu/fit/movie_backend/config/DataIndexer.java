package nlu.fit.movie_backend.config;

import nlu.fit.movie_backend.document.MediaContentDocument;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.repository.elasticsearchrepository.MediaContentSearchRepository;
import nlu.fit.movie_backend.repository.jpa.MediaContentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

@Component
public class DataIndexer implements CommandLineRunner {
    @Autowired
    private MediaContentSearchRepository mediaContentSearchRepository;
    @Autowired
    private MediaContentRepository mediaContentRepository;

    @Override
    public void run(String... args) throws Exception {
        if (mediaContentSearchRepository.count() == 0) {
            List<MediaContent> mediaContents = mediaContentRepository.findAll();
            List<MediaContentDocument> indexList = mediaContents.stream().map(m -> {
                Long yearValue = null;

                if (m.getReleaseDate() != null) {
                    yearValue = (long) m.getReleaseDate().getYear();
                } else {
                    yearValue = 0L;
                }
                return new MediaContentDocument(m.getId(), m.getTitle(),m.getBackdropPath(), yearValue);
            }).collect(Collectors.toList());

            mediaContentSearchRepository.saveAll(indexList);
        }
    }
}
