package nlu.fit.movie_backend.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "model_registry")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ModelRegistry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "model_name")
    private String modelName;

    private Double version;

    @Column(name = "model_path")
    private String modelPath;

    private Double rmse;

    private Double mae;

    private Double precision;

    private Double recall;

    @Column(name = "f1_score")
    private Double f1Score;

    @Column(name = "is_active")
    private Boolean isActive = true;

    @Column(name = "job_id")
    private String jobId;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}