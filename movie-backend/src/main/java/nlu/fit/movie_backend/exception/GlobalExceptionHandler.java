package nlu.fit.movie_backend.exception;

import jakarta.persistence.QueryTimeoutException;
import nlu.fit.movie_backend.constants.ErrorCode;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import javax.security.auth.login.AccountLockedException;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(value = AppException.class)
    public ResponseEntity<ApiResponse> handlingAppException(AppException exception) {
        ErrorCode errorCode = exception.getErrorCode();
        return ResponseEntity.status(errorCode.getHttpStatus()).body(
                ApiResponse.builder().code(errorCode.getCode()).message(errorCode.getMessage()).build()
        );
    }

    @ExceptionHandler(value = MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse> handlingValidation(MethodArgumentNotValidException exception) {
        String msg = exception.getBindingResult().getFieldError().getDefaultMessage();
        return ResponseEntity.badRequest().body(
                ApiResponse.builder().code(400).message(msg).build()
        );
    }

    @ExceptionHandler(value = Exception.class)
    public ResponseEntity<ApiResponse> handlingGenericException(Exception exception) {
        return ResponseEntity.internalServerError().body(
                ApiResponse.builder()
                        .code(ErrorCode.UNCATEGORIZED_EXCEPTION.getCode())
                        .message(ErrorCode.UNCATEGORIZED_EXCEPTION.getMessage())
                        .build()
        );
    }

    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<ApiResponse<Void>> handleDatabaseError(DataAccessException ex) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(ApiResponse.<Void>builder()
                        .code(ErrorCode.DATABASE_ERROR.getCode())
                        .message("Hệ thống cơ sở dữ liệu đang bảo trì")
                        .build());
    }

    // Xử lý luồng phụ: Mất kết nối / Timeout (Ví dụ gọi sang Service khác như Chatbot)
    @ExceptionHandler(QueryTimeoutException.class)
    public ResponseEntity<ApiResponse<Void>> handleTimeout() {
        return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT)
                .body(ApiResponse.<Void>builder()
                        .code(9004)
                        .message("Kết nối quá hạn, vui lòng thử lại sau")
                        .build());
    }
}
