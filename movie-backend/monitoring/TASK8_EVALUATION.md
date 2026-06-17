# Task 8 - [Evaluation] Track Online Metrics (CTR/Conversion) via Analytics API

Mục tiêu: Ghi nhận impression, click, conversion để đo CTR & conversion rate theo thuật toán.

1) Database schema (Postgres)

```sql
CREATE TABLE recommendation_metrics (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR,
  movie_id VARCHAR,
  recommended_by VARCHAR,
  recommended_at TIMESTAMP,
  impression BOOLEAN DEFAULT FALSE,
  clicked BOOLEAN DEFAULT FALSE,
  clicked_at TIMESTAMP,
  liked BOOLEAN DEFAULT FALSE,
  watched_duration INTEGER,
  converted BOOLEAN DEFAULT FALSE,
  conversion_type VARCHAR,
  created_at TIMESTAMP DEFAULT now()
);
```

2) API endpoints (movie-backend)
- POST /api/analytics/impression
- POST /api/analytics/click
- POST /api/analytics/conversion
- GET /api/analytics/metrics?algo=vector&period=24h

3) Flow
- Frontend sends impression when recommendations are rendered (include recommended_by)
- On click, frontend sends click and backend marks clicked=true
- If click leads to purchase/like/watch, send conversion with type

4) Aggregations & jobs
- Hourly aggregation job (cron) to compute:
  - impressions, clicks, CTR = clicks/impressions
  - conversions, conversion_rate = conversions/clicks
  - avg_watch_time
- Store aggregated results in Redis for fast dashboard

5) Sample aggregation SQL
```sql
SELECT recommended_by,
  sum(case when impression then 1 else 0 end) as impressions,
  sum(case when clicked then 1 else 0 end) as clicks,
  ROUND(100.0 * sum(case when clicked then 1 else 0 end) / NULLIF(sum(case when impression then 1 else 0 end),0),2) as ctr
FROM recommendation_metrics
WHERE created_at >= now() - interval '24 hours'
GROUP BY recommended_by;
```

6) Integration with Grafana
- Expose aggregation results via /api/analytics/metrics JSON
- Prometheus: export gauges for CTRs if desired

7) Tests & Validation
- Simulate impressions+clicks to verify CTR calculations
- Compare online metrics vs offline ground truth samples

8) Notes
- Ensure event deduplication by event_id
- Consider GDPR/consent flags for tracking

--
Hết file TASK8_EVALUATION.md
