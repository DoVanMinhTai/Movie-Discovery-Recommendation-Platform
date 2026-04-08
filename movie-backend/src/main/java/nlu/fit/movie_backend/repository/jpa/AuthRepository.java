package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AuthRepository extends JpaRepository<User,Long> {
    User findByEmail(String email);

}
