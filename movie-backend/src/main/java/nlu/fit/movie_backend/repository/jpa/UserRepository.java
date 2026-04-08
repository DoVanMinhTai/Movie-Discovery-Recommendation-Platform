package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User,Long> {
    Optional<User> findByEmail(String email);

    boolean existsByEmailAndIsDeletedFalse(String email);
}
