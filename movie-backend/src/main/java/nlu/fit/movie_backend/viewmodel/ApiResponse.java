package nlu.fit.movie_backend.viewmodel;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;
import lombok.experimental.FieldDefaults;
import nlu.fit.movie_backend.constants.ErrorCode;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    @Builder.Default
    int code = 1000;
    String message;
    T result;

    public static <T> ApiResponse<T> success(ErrorCode errorCode, T result) {
        return ApiResponse.<T>builder().code(errorCode.getCode()).message(errorCode.getMessage()).result(result).build();
    }
}