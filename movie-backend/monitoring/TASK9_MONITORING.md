# Task 9 - [Monitoring] Expand Grafana Dashboards for Model Accuracy and API Latency Metrics

Mục tiêu: Triển khai Prometheus + Grafana; thêm dashboards giám sát latency, model accuracy, stream health.

1) Thêm Prometheus & Grafana vào docker-compose
- prometheus:
  image: prom/prometheus:latest
  ports: ["9090:9090"]
  volumes: ["./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml"]
- grafana:
  image: grafana/grafana:latest
  ports: ["3000:3000"]
  volumes: ["./monitoring/grafana:/var/lib/grafana"]

2) prometheus.yml (ví dụ)
```
scrape_configs:
  - job_name: 'movie-backend'
    static_configs:
      - targets: ['movie-backend:8080']
  - job_name: 'stream_worker'
    static_configs:
      - targets: ['stream-worker:8000']
  - job_name: 'elasticsearch'
    metrics_path: /_prometheus/metrics
    static_configs:
      - targets: ['elasticsearch:9200']
```

3) Instrument backend (Java)
- Thêm micrometer + prometheus registry (sample endpoints /actuator/prometheus)
- Metrics to expose:
  - http_server_requests (latency histograms)
  - es_query_duration_ms (custom)
  - cache_hit_rate (custom gauge)

4) Instrument Python worker
- Use prometheus_client to expose /metrics endpoint
- Counters/histograms: events_processed, processing_latency_seconds, redis_update_time_seconds

5) Grafana Dashboards (panels)
- API latency: p50/p95/p99 (histogram aggregation)
- ES query latency (ms)
- Cache hit rate %
- CTR & conversion rate over time (from analytics API or Prometheus gauges)
- Stream throughput (events/sec)
- Consumer lag (monitored via Kafka/Redpanda metrics)

6) Alerts (Prometheus alert rules)
- api_latency_high: if 95th_percentile_http_server_requests > 500ms for 5m
- error_rate_high: if http_errors / total_requests > 0.05 for 5m
- stream_lag_high: if kafka_consumer_lag > 5000 messages
- ctr_drop: if CTR drops >20% vs previous hour (need ratio metric)

7) Dashboard provisioning
- Export panels as JSON and mount into Grafana provisioning folder
- Configure data source (Prometheus) in provisioning

8) Tests
- Verify metrics endpoints reachable
- Verify dashboards show live data
- Fire synthetic load to ensure alerts trigger

9) Notes
- Keep retention policy in Prometheus reasonable (30d)
- Protect Grafana with strong admin creds

--
Hết file TASK9_MONITORING.md
