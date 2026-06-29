package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/health")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class HealthCheckController {
    
    private final DataSource dataSource;

    @GetMapping
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        
        health.put("status", "UP");
        health.put("timestamp", System.currentTimeMillis());
        health.put("application", "Movie Recommender System");
        health.put("version", "1.0.0");
        
        try (Connection conn = dataSource.getConnection()) {
            health.put("database", "UP");
            health.put("databaseType", conn.getMetaData().getDatabaseProductName());
            health.put("databaseVersion", conn.getMetaData().getDatabaseProductVersion());
        } catch (Exception e) {
            health.put("database", "DOWN");
            health.put("databaseError", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(health);
        }

        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long usedMemory = totalMemory - freeMemory;
        long maxMemory = runtime.maxMemory();
        
        Map<String, String> memory = new HashMap<>();
        memory.put("total", formatBytes(totalMemory));
        memory.put("used", formatBytes(usedMemory));
        memory.put("free", formatBytes(freeMemory));
        memory.put("max", formatBytes(maxMemory));
        memory.put("usagePercent", String.format("%.2f%%", (usedMemory * 100.0 / totalMemory)));
        health.put("memory", memory);
        
        return ResponseEntity.ok(health);
    }
    

    @GetMapping("/ready")
    public ResponseEntity<Map<String, String>> readinessCheck() {
        Map<String, String> ready = new HashMap<>();
        
        try (Connection conn = dataSource.getConnection()) {
            ready.put("status", "READY");
            ready.put("message", "Application is ready to serve traffic");
            return ResponseEntity.ok(ready);
        } catch (Exception e) {
            ready.put("status", "NOT_READY");
            ready.put("reason", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(ready);
        }
    }

    @GetMapping("/live")
    public ResponseEntity<Map<String, String>> livenessCheck() {
        Map<String, String> live = new HashMap<>();
        live.put("status", "ALIVE");
        live.put("message", "Application is running");
        return ResponseEntity.ok(live);
    }

    private String formatBytes(long bytes) {
        long mb = bytes / (1024 * 1024);
        return mb + " MB";
    }
}
