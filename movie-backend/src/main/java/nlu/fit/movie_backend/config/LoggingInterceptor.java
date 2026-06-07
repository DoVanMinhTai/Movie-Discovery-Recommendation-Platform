package nlu.fit.movie_backend.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Slf4j
@Component
public class LoggingInterceptor implements HandlerInterceptor {
    
    private static final String START_TIME = "startTime";
    private static final long SLOW_REQUEST_THRESHOLD = 1000;
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, 
                            Object handler) {
        long startTime = System.currentTimeMillis();
        request.setAttribute(START_TIME, startTime);
        
        log.info("→ Request: {} {} from {}", 
                request.getMethod(), 
                request.getRequestURI(), 
                request.getRemoteAddr());
        
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                               HttpServletResponse response, 
                               Object handler, 
                               Exception ex) {
        Long startTime = (Long) request.getAttribute(START_TIME);
        if (startTime == null) {
            return;
        }
        
        long endTime = System.currentTimeMillis();
        long responseTime = endTime - startTime;
        
        String logMessage = String.format("← Response: %s %s - Status: %d - Time: %dms", 
                request.getMethod(), 
                request.getRequestURI(), 
                response.getStatus(), 
                responseTime);
        
        if (responseTime > SLOW_REQUEST_THRESHOLD) {
            log.warn("SLOW REQUEST: {} ({}ms)", request.getRequestURI(), responseTime);
        } else {
            log.info(logMessage);
        }
        
        if (ex != null) {
            log.error("Request failed: {} {} - Error: {}",
                    request.getMethod(), 
                    request.getRequestURI(), 
                    ex.getMessage(), 
                    ex);
        }
        
        int status = response.getStatus();
        if (status >= 400 && status < 500) {
            log.warn("Client error: {} {} - Status: {}",
                    request.getMethod(), 
                    request.getRequestURI(), 
                    status);
        } else if (status >= 500) {
            log.error("Server error: {} {} - Status: {}",
                    request.getMethod(), 
                    request.getRequestURI(), 
                    status);
        }
    }
}
