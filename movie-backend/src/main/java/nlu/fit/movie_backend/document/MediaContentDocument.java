package nlu.fit.movie_backend.document;

import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.elasticsearch.annotations.*;

@Document(indexName = "mediacontent")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class MediaContentDocument {

    @Id
    private Long id;

    @MultiField(
            mainField = @Field(type = FieldType.Text),
            otherFields = { @InnerField(suffix = "keyword", type = FieldType.Keyword) }
    )
    private String title;

    @Field(name = "backdrop_path")
    private String backdropPath;

    private Long releaseDate;
}
