package nlu.fit.movie_backend.exception;

import lombok.Getter;
import nlu.fit.movie_backend.constants.ErrorCode;

@Getter
public class AppException extends RuntimeException {

    public AppException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    private ErrorCode errorCode;

    public void setErrorCode(ErrorCode errorCode) {
        this.errorCode = errorCode;
    }
}
