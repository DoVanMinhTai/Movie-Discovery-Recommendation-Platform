package nlu.fit.movie_backend.constants;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ErrorCode {
    SUCCESS(1000, "Operation successful", HttpStatus.OK),
    REGISTER_SUCCESS(1001, "User registered successfully", HttpStatus.CREATED),
    LOGIN_SUCCESS(1002, "Login successful", HttpStatus.OK),
    UPDATE_SUCCESS(1003, "Update data successfully", HttpStatus.OK),

    USER_EXISTED(1001, "User already exists", HttpStatus.BAD_REQUEST),
    USER_NOT_EXISTED(1002, "User does not exist", HttpStatus.NOT_FOUND),
    INVALID_CREDENTIALS(1003, "Invalid email or password", HttpStatus.UNAUTHORIZED),
    UNAUTHENTICATED(1004, "Unauthenticated", HttpStatus.UNAUTHORIZED),
    ACCOUNT_LOCKED(1005, "Account is locked", HttpStatus.LOCKED),
    USER_NOT_FOUND(1006, "User profile not found", HttpStatus.NOT_FOUND),

    MEDIA_CONTENT_NOT_FOUND(2001, "Media content not found", HttpStatus.NOT_FOUND),
    MOVIE_NOT_FOUND(1009, "Movie not found", HttpStatus.NOT_FOUND),
    GENRE_NOT_FOUND(1011, "Genre not found", HttpStatus.NOT_FOUND),

    EMAIL_INVALID(3001, "Invalid email format", HttpStatus.BAD_REQUEST),
    PASSWORD_INVALID(3002, "Password must be at least 8 characters", HttpStatus.BAD_REQUEST),

    CHATBOT_SERVICE_UNAVAILABLE(9001, "Service Unavailable", HttpStatus.SERVICE_UNAVAILABLE),
    INVALID_CHAT_REQUEST(9002, "Message Error", HttpStatus.BAD_REQUEST),
    MAX_CHAT_LIMIT_REACHED(9003, "Limited", HttpStatus.TOO_MANY_REQUESTS),

    DATABASE_ERROR(9000, "Database connection failed", HttpStatus.SERVICE_UNAVAILABLE),
    UNCATEGORIZED_EXCEPTION(9999, "Uncategorized error", HttpStatus.INTERNAL_SERVER_ERROR),
    INVALID_KEY(8888, "Uncategorized error", HttpStatus.BAD_REQUEST),
    ;

    ErrorCode(int code, String message, HttpStatus httpStatus) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
    }

    private final int code;
    private final String message;
    private final HttpStatus httpStatus;
}
