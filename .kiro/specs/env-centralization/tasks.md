# Implementation Plan: env-centralization

## Overview

Tập trung hóa toàn bộ cấu hình môi trường của Media Recommender System vào một root-level `.env` duy nhất. Kế hoạch thực hiện theo thứ tự: (1) dọn dẹp `.gitignore` và git tracking, (2) tạo file `.env.example` tại root và từng service, (3) cập nhật `docker-compose.yml` với explicit env blocks, (4) loại bỏ auto-loading trong Python services, (5) sửa Dockerfile của `movie-frontend` và thêm `.dockerignore` cho `movie-chatbot`, (6) viết property-based tests bằng Hypothesis để kiểm chứng các invariants.

---

## Tasks

- [x] 1. Cập nhật `.gitignore` và dọn dẹp git tracking

  - [x] 1.1 Cập nhật root `.gitignore` với đầy đủ patterns bảo vệ credentials
    - Thêm root-anchored patterns `/.env` và `/.env.prod` (nếu chưa có)
    - Thêm glob patterns `**/.env`, `**/.env.local`, `**/.env.production`, `**/.env.prod`
    - Đảm bảo negation rule `!.env.example` xuất hiện SAU mọi wildcard `*.env*` rule
    - Thêm pattern `!**/.env.example` để cho phép commit `.env.example` ở mọi subdirectory
    - File cần sửa: `.gitignore`
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 1.2 Xóa các Service_Env_File đang bị git track
    - Chạy `git rm --cached movie-backend/.env movie-backend/.env.production movie-chatbot/.env movie-recommendation/.env movie-frontend/.env` (chỉ với các file đang được track)
    - Verify bằng `git ls-files | grep -E '\.env$|\.env\.local$|\.env\.production$'` trả về rỗng
    - File cần sửa: không có — chỉ thao tác git index
    - _Requirements: 7.4, 7.5_

  - [ ]* 1.3 Viết property test: Property 7 — `.env.example` không bao giờ bị git-ignore
    - **Property 7: `.env.example` Files Are Never Git-Ignored**
    - **Validates: Requirements 7.2**
    - Tạo file `tests/test_env_centralization.py` với test framework (pytest + Hypothesis)
    - Test dùng `st.sampled_from(glob("**/.env.example"))` và kiểm tra `git check-ignore` trả về empty
    - Tag: `# Feature: env-centralization, Property 7: .env.example files are never git-ignored`

  - [ ]* 1.4 Viết property test: Property 8 — Không có real `.env` file nào bị git track
    - **Property 8: No Real `.env` Files Are Git-Tracked**
    - **Validates: Requirements 7.4, 7.5**
    - Test kiểm tra `git ls-files` output không chứa file match pattern `.env`, `.env.local`, `.env.production`, `.env.prod`
    - Tag: `# Feature: env-centralization, Property 8: No real .env files are git-tracked`

- [x] 2. Tạo root `.env.example` và per-service `.env.example` files

  - [x] 2.1 Tạo root `.env.example` với đầy đủ variables và placeholder values
    - Tạo file `root .env.example` tại project root (không phải `.env` thật)
    - Tổ chức thành 9 sections với comment headers: `# === DATABASE ===`, `# === ELASTICSEARCH ===`, `# === SERVICE PORTS ===`, `# === INTER-SERVICE URLS ===`, `# === API KEYS ===`, `# === CORS ===`, `# === FRONTEND ===`, `# === MEMORY LIMITS ===`, `# === JAVA ===`
    - Mỗi variable dùng format placeholder `your_<variable_name>_here` (ví dụ: `DB_PASSWORD=your_db_password_here`)
    - Mỗi variable có inline comment giải thích mục đích và format
    - File phải cover TẤT CẢ variables trong `root .env` hiện tại
    - File cần tạo: `.env.example`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 2.2 Viết property test: Property 3 — `.env.example` completeness
    - **Property 3: `.env.example` Completeness**
    - **Validates: Requirements 5.1, 5.3**
    - Dùng `@given(st.just(parse_env_keys(".env")))` để lấy tập keys từ `.env`
    - Assert mỗi key đó tồn tại trong `.env.example`
    - Tag: `# Feature: env-centralization, Property 3: .env.example completeness`

  - [ ]* 2.3 Viết property test: Property 4 — Không có real credentials trong `.env.example`
    - **Property 4: No Real Credentials in `.env.example`**
    - **Validates: Requirements 5.4**
    - Dùng `@given(st.sampled_from(parse_env_values(".env.example")))` lấy từng value
    - Assert value không match: UUID, base64 > 20 chars, prefix `hf_` / `gsk_`, `bonsaisearch.net`, `supabase.com`, alphanumeric > 8 chars không có placeholder marker
    - Tag: `# Feature: env-centralization, Property 4: No real credentials in .env.example`

  - [x] 2.4 Tạo per-service `.env.example` cho `movie-backend`
    - Tạo `movie-backend/.env.example` liệt kê: `DB_URL`, `DB_USER`, `DB_PASSWORD`, `ES_URL`, `ES_HOST`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, `JAVA_OPTS`
    - Mỗi variable dùng sentinel placeholder `<YOUR_VALUE_HERE>` và có inline comment
    - File cần tạo: `movie-backend/.env.example`
    - _Requirements: 3.2, 3.3_

  - [x] 2.5 Tạo per-service `.env.example` cho `movie-chatbot`
    - Tạo `movie-chatbot/.env.example` liệt kê: `ES_HOST`, `ES_URL`, `GROQ_API_KEY`, `GROQ_MODEL`, `HF_TOKEN`, `CHATBOT_PORT`
    - Mỗi variable dùng sentinel placeholder `<YOUR_VALUE_HERE>` và có inline comment
    - File cần tạo: `movie-chatbot/.env.example`
    - _Requirements: 3.2, 3.3_

  - [x] 2.6 Tạo per-service `.env.example` cho `movie-recommendation`
    - Tạo `movie-recommendation/.env.example` liệt kê: `DATABASE_URL`, `ES_HOST`, `ES_URL`, `HF_TOKEN`, `CHATBOT_URL`, `BACKEND_URL`
    - Lưu ý: `DATABASE_URL` khác với `DB_URL` — đây là format `postgresql://user:pass@host:port/db`
    - Mỗi variable dùng sentinel placeholder `<YOUR_VALUE_HERE>` và có inline comment
    - File cần tạo: `movie-recommendation/.env.example`
    - _Requirements: 3.2, 3.3_

  - [x] 2.7 Tạo per-service `.env.example` cho `movie-frontend`
    - Tạo `movie-frontend/.env.example` liệt kê: `VITE_API_BASE_URL`
    - Có inline comment giải thích đây là build-time variable, không phải runtime
    - File cần tạo: `movie-frontend/.env.example`
    - _Requirements: 3.2, 3.3_

  - [ ]* 2.8 Viết property test: Property 5 — Per-service `.env.example` coverage
    - **Property 5: Per-Service `.env.example` Coverage**
    - **Validates: Requirements 3.3**
    - Dùng `@given(st.sampled_from(SERVICE_EXPECTED_VARS.items()))` với dict mapping service → expected vars
    - Assert mỗi expected var xuất hiện trong service's `.env.example`
    - Tag: `# Feature: env-centralization, Property 5: Per-service .env.example coverage`

- [x] 3. Cập nhật `docker-compose.yml` với explicit environment blocks

  - [x] 3.1 Loại bỏ `env_file:` khỏi `chatbot` service và thêm explicit `environment:` block
    - Xóa `env_file: - .env` khỏi `chatbot` service
    - Giữ nguyên và đảm bảo `environment:` block chứa ĐÚNG và CHỈ: `PYTHONUNBUFFERED=1`, `ES_HOST=${ES_HOST}`, `ES_URL=${ES_URL}`, `GROQ_API_KEY=${GROQ_API_KEY}`, `GROQ_MODEL=${GROQ_MODEL}`, `HF_TOKEN=${HF_TOKEN}`
    - Sửa `ES_HOST=http://elasticsearch:9200` hardcode thành `ES_HOST=${ES_HOST}` để dùng biến từ `.env`
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 6.1, 6.2_

  - [x] 3.2 Cập nhật `recommendation` service: xóa `env_file:`, explicit `environment:` block đầy đủ
    - Xóa `env_file: - .env` khỏi `recommendation` service
    - Thay thế `environment:` block hiện tại bằng block chứa ĐÚNG và CHỈ: `DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}`, `ES_HOST=${ES_HOST}`, `ES_URL=${ES_URL}`, `HF_TOKEN=${HF_TOKEN}`, `CHATBOT_URL=${CHATBOT_URL}`, `BACKEND_URL=${BACKEND_URL}`
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 6.1, 6.3_

  - [x] 3.3 Cập nhật `movie-backend` service: xóa `VITE_API_BASE_URL` khỏi environment block
    - Xóa dòng `- VITE_API_BASE_URL=${VITE_API_BASE_URL}` khỏi `movie-backend` service
    - Giữ nguyên tất cả các biến còn lại: `DB_URL`, `DB_USER`, `DB_PASSWORD`, `ES_URL`, `ES_HOST`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, `JAVA_OPTS`
    - Cập nhật `JAVA_OPTS` thành `JAVA_OPTS=${JAVA_OPTS}` để đọc từ `.env` thay vì hardcode
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 6.4, 6.5_

  - [x] 3.4 Cập nhật `movie-frontend` service: xóa `env_file:`, thêm `build.args` cho VITE_*
    - Xóa `env_file: - .env` khỏi `movie-frontend` service
    - Thêm `build.args` block: `args: - VITE_API_BASE_URL=${VITE_API_BASE_URL}`
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 6.1, 4.3_

  - [x] 3.5 Cập nhật `initializer` và `mage` services: thay `ES_HOST=elasticsearch` hardcode bằng `ES_HOST=${ES_HOST}`
    - Trong `initializer` service: đổi `- ES_HOST=elasticsearch` thành `- ES_HOST=${ES_HOST}`
    - Trong `mage` service: đổi `- ES_HOST=elasticsearch` thành `- ES_HOST=${ES_HOST}`
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 8.1, 8.4_

  - [x] 3.6 Thêm `${VAR:?error message}` syntax cho critical variables trong `docker-compose.yml`
    - Cập nhật các biến critical trong postgres, movie-backend, recommendation, chatbot dùng cú pháp fail-fast: ví dụ `${DB_PASSWORD:?DB_PASSWORD is required}`, `${GROQ_API_KEY:?GROQ_API_KEY is required}`
    - Áp dụng cho: `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `GROQ_API_KEY`, `HF_TOKEN`
    - File cần sửa: `docker-compose.yml`
    - _Requirements: 1.5_

  - [ ]* 3.7 Viết property test: Property 9 — ES_HOST nhất quán giữa các services
    - **Property 9: Consistent ES_HOST Across All Docker Compose Services**
    - **Validates: Requirements 8.1, 8.4**
    - Parse `docker-compose.yml` với PyYAML, kiểm tra 5 services ES-connected (`movie-backend`, `chatbot`, `recommendation`, `initializer`, `mage`) đều có `ES_HOST` và giá trị đều reference `${ES_HOST}`
    - Tag: `# Feature: env-centralization, Property 9: Consistent ES_HOST across all DC services`

  - [ ]* 3.8 Viết property test: Property 11 — Chatbot và Recommendation chỉ nhận đúng variables
    - **Property 11: Chatbot and Recommendation Services Receive Only Required Variables**
    - **Validates: Requirements 6.2, 6.3**
    - Parse `docker-compose.yml`, lấy environment keys của `chatbot` và `recommendation`
    - Assert `chatbot` keys ⊆ `{PYTHONUNBUFFERED, ES_HOST, ES_URL, GROQ_API_KEY, GROQ_MODEL, HF_TOKEN}`
    - Assert `recommendation` keys ⊆ `{DATABASE_URL, ES_HOST, ES_URL, HF_TOKEN, CHATBOT_URL, BACKEND_URL}`
    - Tag: `# Feature: env-centralization, Property 11: Chatbot and Recommendation receive only required variables`

- [x] 4. Checkpoint — Kiểm tra docker-compose config
  - Chạy `docker-compose config --quiet` và verify không có unresolved variable warnings
  - Verify `docker-compose config` output cho `chatbot` không còn chứa `DB_URL` hay `FRONTEND_PORT`
  - Verify `docker-compose config` output cho `movie-backend` không còn chứa `VITE_API_BASE_URL`
  - Đặt câu hỏi cho user nếu có vấn đề phát sinh.

- [x] 5. Loại bỏ auto-loading trong Python services

  - [x] 5.1 Sửa `movie-chatbot/app/core/config.py`: xóa `load_project_env()` và `env_file`
    - Xóa toàn bộ function `load_project_env()` (từ `def load_project_env():` đến hết)
    - Xóa dòng gọi `load_project_env()` ở module scope
    - Xóa `from dotenv import load_dotenv` import
    - Trong `SettingsConfigDict`: đổi `env_file=".env"` thành xóa tham số `env_file` hoàn toàn
    - Giữ nguyên `env_file_encoding`, `case_sensitive`, `extra` params
    - File cần sửa: `movie-chatbot/app/core/config.py`
    - _Requirements: 3.5, 4.4_

  - [x] 5.2 Sửa `movie-recommendation/app/core/config.py`: xóa `load_project_env()` và `env_file`
    - Xóa toàn bộ function `load_project_env()` (từ `def load_project_env():` đến hết)
    - Xóa dòng gọi `load_project_env()` ở module scope
    - Xóa `from dotenv import load_dotenv` import
    - Trong `SettingsConfigDict`: đổi `env_file=".env"` thành xóa tham số `env_file` hoàn toàn
    - Lưu ý: field `database_url` đang dùng `validation_alias="DB_URL_PYTHON"` — phải cập nhật thành `validation_alias="DATABASE_URL"` để match với biến Docker Compose inject (`DATABASE_URL=postgresql://...`)
    - File cần sửa: `movie-recommendation/app/core/config.py`
    - _Requirements: 3.5, 4.4_

  - [ ]* 5.3 Viết property test: Property 6 — Không có auto-loading trong Python services
    - **Property 6: No Auto-Loading in Python Services**
    - **Validates: Requirements 3.5, 4.4**
    - Dùng `@given(st.sampled_from(get_tracked_python_files(["movie-chatbot", "movie-recommendation"])))` để lấy từng file Python được git track
    - Assert content không chứa `load_dotenv()` unconditionally ở module scope
    - Assert `SettingsConfigDict` không có `env_file=` set thành non-`None` string
    - Tag: `# Feature: env-centralization, Property 6: No auto-loading in Python services`

  - [ ]* 5.4 Viết property test: Property 10 — Không có hardcoded Bonsai URL trong chatbot source
    - **Property 10: No Hardcoded Bonsai URLs in Chatbot Source**
    - **Validates: Requirements 8.3**
    - Dùng `@given(st.sampled_from(get_tracked_files("movie-chatbot")))` lấy từng git-tracked file
    - Assert content không chứa chuỗi `bonsaisearch.net`
    - Tag: `# Feature: env-centralization, Property 10: No hardcoded Bonsai URLs in chatbot source`

- [x] 6. Sửa `movie-frontend` Dockerfile và thêm `.dockerignore` cho `movie-chatbot`

  - [x] 6.1 Sửa `movie-frontend/Dockerfile`: xóa `COPY .env ../.env`, thêm `ARG`/`ENV` cho VITE_*
    - Xóa dòng `COPY .env ../.env` khỏi Dockerfile
    - Thêm `ARG VITE_API_BASE_URL` trước `COPY . .`
    - Thêm `ENV VITE_API_BASE_URL=$VITE_API_BASE_URL` sau ARG declaration
    - File cần sửa: `movie-frontend/Dockerfile`
    - _Requirements: 4.3, 4.5_

  - [x] 6.2 Tạo `movie-chatbot/.dockerignore` để ngăn copy `.env` vào image
    - Tạo file `movie-chatbot/.dockerignore`
    - Nội dung: `.env`, `.env.*`, `!.env.example`
    - File cần tạo: `movie-chatbot/.dockerignore`
    - _Requirements: 4.6_

- [x] 7. Thiết lập test suite và viết property tests còn lại

  - [x] 7.1 Thiết lập test infrastructure cho property-based tests
    - Tạo `tests/` directory tại project root (nếu chưa có)
    - Tạo `tests/requirements.txt` với: `hypothesis`, `pytest`, `pyyaml`, `python-dotenv`
    - Tạo `tests/__init__.py`
    - Tạo `tests/helpers.py` với helper functions: `parse_env_file(path)`, `parse_env_keys(path)`, `parse_env_values(path)`, `parse_docker_compose(path)`, `get_tracked_python_files(dirs)`, `get_tracked_files(dir)`
    - File cần tạo: `tests/__init__.py`, `tests/helpers.py`, `tests/requirements.txt`
    - _Requirements: — (infrastructure task)_

  - [x] 7.2 Tạo `tests/test_env_centralization.py` — assembly toàn bộ property tests
    - Consolidate tất cả property tests đã viết ở các tasks trước (1.3, 1.4, 2.2, 2.3, 2.8, 3.7, 3.8, 5.3, 5.4) vào một file duy nhất
    - Thêm Property 1 test và Property 2 test (chưa có ở task nào)
    - Đảm bảo mỗi test có tag comment `# Feature: env-centralization, Property N: ...`
    - Đảm bảo mỗi `@given` strategy chạy tối thiểu 100 iterations (`@settings(max_examples=100)`)
    - File cần tạo: `tests/test_env_centralization.py`
    - _Requirements: 1.4, 2.1, 5.1, 5.3, 5.4, 3.3, 3.5, 4.4, 6.2, 6.3, 7.2, 7.4, 8.1, 8.3, 8.4_

  - [ ]* 7.3 Viết property test: Property 1 — Không có duplicate keys trong root `.env`
    - **Property 1: No Duplicate Keys in Root `.env`**
    - **Validates: Requirements 1.4**
    - Dùng `@given(st.just(parse_env_file(".env")))` để lấy list `(key, value)` pairs
    - Assert `len(keys) == len(set(keys))`
    - Tag: `# Feature: env-centralization, Property 1: No duplicate keys in root .env`

  - [ ]* 7.4 Viết property test: Property 2 — Dev và Prod values khác nhau cho sensitive variables
    - **Property 2: Dev and Prod Values Differ for Sensitive Variables**
    - **Validates: Requirements 2.1**
    - Dùng `@given(st.sampled_from(SENSITIVE_VARS))` với 8 biến sensitive đã định nghĩa trong design
    - Parse `.env` và `.env.prod`, assert `dev_value != prod_value` cho mỗi biến
    - Tag: `# Feature: env-centralization, Property 2: Dev and prod values differ for sensitive variables`

- [x] 8. Checkpoint cuối — Đảm bảo tất cả tests pass
  - Chạy `pytest tests/test_env_centralization.py -v` và verify tất cả property tests pass
  - Verify không có `Service_Env_File` nào còn tồn tại: `movie-backend/.env`, `movie-chatbot/.env`, `movie-recommendation/.env`, `movie-frontend/.env`
  - Verify `git ls-files | grep -E '\.env$'` trả về rỗng (chỉ `.env.example` được track)
  - Đặt câu hỏi cho user nếu có vấn đề phát sinh.

---

## Notes

- Tasks đánh dấu `*` là optional — có thể bỏ qua để tiến nhanh đến MVP, nhưng nên thực hiện để đảm bảo correctness
- Task 1.2 là thao tác git, không phải code — thực hiện manually hoặc qua shell command trong coding agent
- Task 5.2 có một chi tiết quan trọng: `validation_alias="DB_URL_PYTHON"` phải đổi thành `validation_alias="DATABASE_URL"` vì Docker Compose inject biến tên `DATABASE_URL`
- Property tests dùng Hypothesis không cần thêm dependency mới vào các service — chỉ cần trong `tests/requirements.txt`
- Sau khi hoàn thành, `docker-compose up` vẫn hoạt động như cũ nếu root `.env` tồn tại với đầy đủ biến

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "7.1"] },
    { "id": 1, "tasks": ["1.3", "1.4", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6"] },
    { "id": 3, "tasks": ["2.8", "3.7", "3.8", "5.1", "5.2", "6.1", "6.2"] },
    { "id": 4, "tasks": ["5.3", "5.4", "7.2"] },
    { "id": 5, "tasks": ["7.3", "7.4"] }
  ]
}
```
