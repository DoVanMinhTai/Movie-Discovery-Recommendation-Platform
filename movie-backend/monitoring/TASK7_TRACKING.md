# Task 7 - [Tracking] Implement Stealth Behavior Tracking (Watch time, CTR)

Mục tiêu: Thêm module JS ở frontend để thu thập watch time, click, impression và gửi về backend (POST /api/events) để Redpanda tiếp nhận.

1) File structure (movie-frontend/src/tracking)
- EventTracker.js
- redpandaClient.js (HTTP sender batching)
- useTracking.js (React hook)

2) Event schema (JSON)
```
{
  "event_id": "uuid",
  "event_type": "click|watch_time|view|like",
  "user_id": "...",
  "movie_id": "...",
  "duration": 45,
  "timestamp": 1680000000,
  "session_id": "...",
  "metadata": {"position": 3, "page":"home"}
}
```

3) EventTracker.js (logic chính)
- initTracker({userId, sessionId})
- trackClick(movieId, position)
- trackView(movieId)
- trackLike(movieId)
- trackWatchTime(movieId, duration)

4) Watch time implementation (IntersectionObserver)
- Tạo observer cho card elements
- Khi visible >=50% bắt đầu timer
- Khi out-of-view hoặc visibility <50% -> pause
- Khi tổng >= 3s -> gửi sự kiện watch_time

Sample (pseudo):
```js
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.intersectionRatio > 0.5) startTimer(id)
    else pauseTimer(id)
  })
}, {threshold: [0.5]})
```

5) Batching & Sender (redpandaClient.js)
- Giữ queue in-memory
- Flush khi size>=10 hoặc time>=5s
- POST /api/events with an array of events
- Retry policy: 3 attempts exponential backoff

6) Backend endpoint (movie-backend)
- POST /api/events
  - Validate events
  - Push each event to Redpanda topic `user-events` (producer)
  - Respond 202

7) Privacy & Performance
- Không gửi PII (họ tên, email)
- Throttle to avoid overload
- Minimal blocking on UI (send async, no await on user action)

8) Tests
- Unit: observer lifecycle, timer
- E2E: simulate scroll + click, ensure POST called and backend enqueues

--
Hết file TASK7_TRACKING.md
