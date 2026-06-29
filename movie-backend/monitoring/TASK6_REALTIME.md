# Task 6 - [Real-time] Implement Real-time Interest Scoring using Redpanda

Mục tiêu: Thiết lập pipeline Redpanda → Python worker để tính score sở thích (genres) theo thời gian thực và lưu vào Redis.

1) Yêu cầu trước
- Redpanda (Kafka-compatible) hoặc Kafka client
- Redis
- Python 3.10+, pip
- Thư viện: confluent-kafka, redis, prometheus_client

2) Thêm Redpanda vào docker-compose (ví dụ):

services:
  redpanda:
    image: vectorized/redpanda:latest
    container_name: redpanda
    command: ["redpanda", "start", "--overprovisioned", "--smp 1", "--memory 1G", "--reserve-memory 0M"]
    ports:
      - "9092:9092"
      - "9644:9644"
    networks:
      - movie-net

Tạo topics: user-events, interest-scores (tooling: rpk or admin API)

3) Python Stream Worker - cấu trúc thư mục (movie-recommendation/stream_worker)
- Dockerfile
- requirements.txt
- main.py
- consumer.py
- scorer.py
- redis_client.py
- metrics.py

requirements.txt
```
confluent-kafka
redis
prometheus-client
python-dotenv
```

4) consumer.py (outline)
- Kết nối tới Redpanda bằng confluent_kafka.Consumer
- Poll events từ topic `user-events`
- Parse theo schema (event_type, user_id, movie_id, metadata)
- Gửi sang scorer.compute_score(event) → nhận dict scores
- Update Redis: HSET user:{user_id}:interests field per genre + timestamp
- Publish updated score nếu cần

5) scorer.py (logic cơ bản)
- weights: click=0.5, watch_30s=1.0, watch_2min=1.5, like=2.0
- Dùng exponential decay: score *= exp(-lambda * age_seconds)
- Map movie -> genres (cần cache metadata từ DB hoặc ES)
- Aggregate per-genre

6) redis_client.py
- Key: user:{user_id}:interests (HASH)
- Fields: genre names (float), last_updated (ts)
- TTL: 7 days (EXPIRE)

7) API integration
- Thay đổi endpoint /recommend:
  - Lấy user interests từ Redis, nếu có convert sang dense vector (sắp xếp genres theo danh sách cố định)
  - Gửi vector làm kNN query cho Elasticsearch
  - Fallback: nếu không có Redis → dùng existing user vector từ DB/ES

8) Metrics & Observability
- Expose Prometheus metrics: events_processed, processing_latency_ms, redis_update_latency
- Ghi log khi event parsing fail

9) Tests
- Unit: scorer.compute_score với nhiều event combo
- Integration: phát sự kiện mẫu vào Redpanda → kiểm tra Redis key updated
- Performance: sao chép events load test ~1000 eps, đo latency

10) Lưu ý vận hành
- Tuning của decay và weights cần A/B test
- Bảo đảm idempotency: event_id để tránh double-processing
- Backup/consumer group để scale

--
Hết file TASK6_REALTIME.md
