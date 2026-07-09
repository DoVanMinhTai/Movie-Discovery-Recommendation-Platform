# Design Document: env-centralization

## Overview

Tính năng này tập trung hóa toàn bộ cấu hình môi trường của Media Recommender System vào một root-level `.env` duy nhất, loại bỏ các per-service `.env` files, tách biệt rõ ràng cấu hình dev/prod, và đảm bảo các production deployments chỉ nhận biến môi trường từ platform dashboards (Render, Hugging Face Spaces, Vercel).

### Goals

- **Single source of truth**: Một file `.env` duy nhất tại root cho toàn bộ Docker Compose stack.
- **Zero business logic changes**: Chỉ thay đổi cơ chế nạp config, không thay đổi logic nghiệp vụ.
- **Platform-agnostic production**: Không có `.env` file nào được load tự động trong production containers.
- **Explicit variable injection**: Docker Compose chỉ truyền đúng biến mỗi service cần, không dump toàn bộ `.env`.
- **Backward compatibility**: `docker-compose up` vẫn hoạt động như cũ với developer sau khi thay đổi.

### Non-Goals

- Không thay đổi secret management (không giới thiệu Vault, AWS Secrets Manager, v.v.).
- Không thay đổi kiến trúc service hoặc giao tiếp giữa services.
- Không thêm dependency mới vào bất kỳ service nào.

---

## Architecture

Kiến trúc hiện tại có hai vấn đề chính:

1. **Phân tán config**: Mỗi service có `.env` riêng, dẫn đến giá trị trùng lặp và không nhất quán.
2. **Auto-loading trong application code**: Python services tự crawl lên project root và gọi `load_dotenv()`, điều này hoạt động khi mount volume nhưng gây ra hành vi không mong muốn trên HF Spaces.

Sau khi thay đổi, luồng cấu hình sẽ như sau:

```mermaid
graph TD
    subgraph "Local Dev"
        ENV[".env (root)"] --> DC["docker-compose.yml"]
        DC -->|explicit env vars| PG["postgres"]
        DC -->|explicit env vars| BE["movie-backend"]
        DC -->|explicit env vars| CB["movie-chatbot"]
        DC -->|explicit env vars| RC["movie-recommendation"]
        DC -->|explicit env vars| FE["movie-frontend (build)"]
        DC -->|explicit env vars| INIT["initializer"]
        DC -->|explicit env vars| MAGE["mage"]
        DC -->|explicit env vars| ES["elasticsearch"]
    end

    subgraph "Production"
        RENDER["Render Dashboard"] -->|system env vars| BE_PROD["movie-backend"]
        HF["HF Secrets"] -->|system env vars| CB_PROD["movie-chatbot"]
        HF -->|system env vars| RC_PROD["movie-recommendation"]
        VERCEL["Vercel Dashboard"] -->|build-time VITE_*| FE_PROD["movie-frontend"]
    end
```

**Sự thay đổi then chốt**: Các Python services không còn tự đọc file `.env` — chúng nhận biến thông qua system environment, dù là từ Docker Compose (local) hay platform dashboard (production).

---

## Components and Interfaces

### 1. Root `.env` File (nguồn truth duy nhất)

File duy nhất được đọc bởi Docker Compose cho local development. Được tổ chức thành các sections có comment header để dễ đọc. **Không được commit vào git.**

**Sections và biến:**

| Section | Variables |
|---|---|
| DATABASE | `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`, `DB_URL` (JDBC), `DB_URL_PYTHON` |
| ELASTICSEARCH | `ES_HOST`, `ES_URL`, `ES_PORT_9200`, `ES_PORT_9300`, `ES_USERNAME`, `ES_PASSWORD` |
| SERVICE PORTS | `BACKEND_PORT`, `CHATBOT_PORT`, `RECOMMENDATION_PORT`, `FRONTEND_PORT` |
| INTER-SERVICE URLS | `CHATBOT_URL`, `RECO_URL`, `BACKEND_URL` |
| API KEYS | `TMDB_API_KEY`, `HF_TOKEN`, `GROQ_API_KEY`, `GROQ_MODEL` |
| CORS | `APP_CORS_ALLOWED_ORIGINS` |
| FRONTEND | `VITE_API_BASE_URL` |
| MEMORY LIMITS | `MEM_LIMIT_POSTGRES`, `MEM_LIMIT_INITIALIZER`, `MEM_LIMIT_ES`, `MEM_LIMIT_API`, `MEM_LIMIT`, `MEM_LIMIT_FRONTEND` |
| JAVA | `JAVA_OPTS` |

**Dev values (Docker-internal hostnames):**
```
ES_HOST=elasticsearch
ES_URL=http://elasticsearch:9200
CHATBOT_URL=http://movie-chatbot:8001
RECO_URL=http://movie-recommendation:8002
BACKEND_URL=http://movie-backend:8080
```

### 2. Root `.env.prod` File (production reference)

Chứa production credentials và hostnames. **Không được commit vào git.** Chỉ dùng làm tài liệu tham chiếu — không được load tự động bởi bất kỳ service nào.

**Prod values (external hostnames):**
```
ES_HOST=<bonsai-cluster>.bonsaisearch.net:443
ES_URL=https://<user>:<pass>@<bonsai-cluster>.bonsaisearch.net
CHATBOT_URL=https://dotai05102004-movie-chatbot.hf.space
RECO_URL=https://dotai05102004-movie-recommendation.hf.space
```

### 3. Root `.env.example` File (onboarding documentation)

Chứa tất cả variable names với placeholder values. **Được commit vào git.** Là hướng dẫn onboarding cho developer mới.

Format placeholder: `VARIABLE_NAME=your_variable_name_here`

Mỗi biến phải có inline comment giải thích mục đích và format.

### 4. Per-service `.env.example` Files

Mỗi service subdirectory có `.env.example` riêng liệt kê chỉ các biến mà service đó đọc tại runtime. **Được commit vào git.**

| Service | Variables trong `.env.example` |
|---|---|
| `movie-backend` | `DB_URL`, `DB_USER`, `DB_PASSWORD`, `ES_URL`, `ES_HOST`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, `JAVA_OPTS` |
| `movie-chatbot` | `ES_HOST`, `ES_URL`, `GROQ_API_KEY`, `GROQ_MODEL`, `HF_TOKEN`, `CHATBOT_PORT` |
| `movie-recommendation` | `DATABASE_URL`, `ES_HOST`, `ES_URL`, `HF_TOKEN`, `CHATBOT_URL`, `BACKEND_URL` |
| `movie-frontend` | `VITE_API_BASE_URL` |

### 5. `docker-compose.yml` — Explicit Variable Injection

Thay thế `env_file: .env` bằng explicit `environment:` blocks cho từng service, chỉ truyền đúng biến cần thiết.

**Thay đổi cụ thể:**

**`chatbot` service** — xóa `env_file: .env`, thay bằng:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - ES_HOST=http://elasticsearch:9200
  - ES_URL=http://elasticsearch:9200
  - GROQ_API_KEY=${GROQ_API_KEY}
  - GROQ_MODEL=${GROQ_MODEL}
  - HF_TOKEN=${HF_TOKEN}
```

**`recommendation` service** — xóa `env_file: .env`, thay bằng:
```yaml
environment:
  - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
  - ES_HOST=${ES_HOST}
  - ES_URL=${ES_URL}
  - HF_TOKEN=${HF_TOKEN}
  - CHATBOT_URL=${CHATBOT_URL}
  - BACKEND_URL=${BACKEND_URL}
```

**`movie-backend` service** — xóa `VITE_API_BASE_URL` khỏi environment block:
```yaml
environment:
  - DB_URL=${DB_URL}
  - DB_USER=${DB_USER}
  - DB_PASSWORD=${DB_PASSWORD}
  - ES_URL=${ES_URL}
  - ES_HOST=${ES_HOST}
  - CHATBOT_URL=${CHATBOT_URL}
  - RECO_URL=${RECO_URL}
  - APP_CORS_ALLOWED_ORIGINS=${APP_CORS_ALLOWED_ORIGINS}
  - JAVA_OPTS=${JAVA_OPTS}
  # VITE_API_BASE_URL removed — frontend build-time only
```

**`movie-frontend` service** — xóa `env_file: .env`. Build-time VITE_* vars được truyền qua `build.args`:
```yaml
build:
  context: ./movie-frontend
  dockerfile: Dockerfile
  args:
    - VITE_API_BASE_URL=${VITE_API_BASE_URL}
```

**`initializer` và `mage` services** — thay `ES_HOST=elasticsearch` hardcode bằng `ES_HOST=${ES_HOST}`:
```yaml
# initializer
environment:
  - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
  - ES_HOST=${ES_HOST}

# mage
environment:
  - ES_HOST=${ES_HOST}
  - ES_PORT_9200=${ES_PORT_9200}
  # ... other vars
```

### 6. Python `config.py` Changes (chatbot & recommendation)

**Loại bỏ hai cơ chế auto-loading:**

1. **`load_project_env()` function**: Xóa toàn bộ function và call `load_project_env()` tại module level.
2. **`SettingsConfigDict(env_file=".env")`**: Thay bằng `env_file=None` hoặc xóa tham số `env_file`.

**Sau thay đổi, `config.py` chỉ đọc từ system environment:**
```python
# BEFORE (auto-loads .env file):
load_project_env()  # <-- REMOVE THIS
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", ...)  # <-- REMOVE env_file

# AFTER (reads from system environment only):
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
        # env_file removed — relies solely on injected environment variables
    )
```

Pydantic-settings tự động đọc `os.environ` khi không có `env_file`, nên không cần thêm code nào.

### 7. `movie-frontend` Dockerfile Changes

**Xóa** dòng `COPY .env ../.env` vì:
- Local dev: VITE_* vars được truyền qua Docker Compose `build.args`.
- Production (Vercel): Vercel inject VITE_* vars trực tiếp vào build environment từ dashboard.

**Thêm** `ARG` instruction để nhận build-time vars:
```dockerfile
# BEFORE:
COPY . .
COPY .env ../.env   # <-- REMOVE THIS
RUN npm run build

# AFTER:
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY . .
RUN npm run build
```

### 8. `movie-chatbot` `.dockerignore` File

Vì `movie-chatbot/Dockerfile` dùng `COPY . .`, cần tạo `.dockerignore` để ngăn copy các file `.env`:
```
.env
.env.*
!.env.example
```

### 9. `.gitignore` Updates

**Thêm** các patterns còn thiếu:
```gitignore
# Root-anchored patterns (thêm vào)
/.env
/.env.prod

# Service subdirectory patterns (thêm vào)
**/.env
**/.env.local
**/.env.production
**/.env.prod

# .env.example luôn được track (giữ nguyên)
!.env.example
**/.env.example
```

---

## Data Models

### Environment Variable Classification

Mỗi biến được phân loại theo scope và lifecycle:

```
EnvVariable {
  name: string            # e.g., "ES_HOST"
  scope: ServiceScope[]   # which services use it
  lifecycle: "build-time" | "runtime"
  sensitivity: "public" | "secret"
  dev_value_type: "docker-internal" | "localhost" | "constant"
  prod_value_type: "external-url" | "api-key" | "constant"
}

ServiceScope = "postgres" | "elasticsearch" | "movie-backend" | 
               "movie-chatbot" | "movie-recommendation" | 
               "movie-frontend" | "initializer" | "mage"
```

**Variable scope mapping:**

| Variable | Services | Lifecycle | Sensitivity |
|---|---|---|---|
| `DB_URL` | movie-backend | runtime | secret |
| `DB_URL_PYTHON` | movie-recommendation, initializer, mage | runtime | secret |
| `ES_HOST` | ALL ES-connected | runtime | public |
| `ES_URL` | movie-backend, chatbot, recommendation | runtime | secret (prod has auth) |
| `ES_USERNAME` / `ES_PASSWORD` | movie-backend (optional), chatbot (optional) | runtime | secret |
| `GROQ_API_KEY` | movie-chatbot | runtime | secret |
| `HF_TOKEN` | movie-chatbot, movie-recommendation | runtime | secret |
| `VITE_API_BASE_URL` | movie-frontend only | **build-time** | public |
| `JAVA_OPTS` | movie-backend | runtime | public |

### Config Loading Flow (After Change)

```
Local Dev:
  root .env → docker-compose.yml (variable substitution) → per-service environment → OS env in container → pydantic-settings Settings()

Production:
  Platform Dashboard → OS env in container → pydantic-settings Settings()
```

In both cases, `Settings()` reads from `os.environ` only — no file I/O at application startup.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: No Duplicate Keys in Root `.env`

*For any* variable key name that appears in `root .env`, it SHALL appear exactly once. No key may be defined multiple times, regardless of how many services reference it.

**Validates: Requirements 1.4**

---

### Property 2: Dev and Prod Values Differ for Sensitive Variables

*For any* of the 8 environment-sensitive variables (`DB_URL`, `DB_URL_PYTHON`, `ES_HOST`, `ES_URL`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, `FRONTEND_PORT`), the value in `root .env` SHALL NOT be equal to the value in `root .env.prod`.

**Validates: Requirements 2.1**

---

### Property 3: `.env.example` Completeness

*For any* variable key K that exists in `root .env`, K SHALL also exist in `root .env.example`. The example file must be a superset of all keys in the real `.env`.

**Validates: Requirements 5.1, 5.3**

---

### Property 4: No Real Credentials in `.env.example`

*For any* variable entry in `root .env.example`, its value SHALL NOT match any real credential pattern: no UUID, no base64-encoded string longer than 20 characters, no string starting with `hf_` or `gsk_`, no string matching a production hostname (e.g., `bonsaisearch.net`, `supabase.com`), and no string that looks like a password (alphanumeric sequence > 8 chars without a placeholder marker).

**Validates: Requirements 5.4**

---

### Property 5: Per-Service `.env.example` Coverage

*For any* environment variable that a service reads at runtime (via `os.environ` or pydantic-settings field definitions), that variable SHALL appear in the corresponding service's `.env.example` file with a placeholder value matching the format `<YOUR_VALUE_HERE>` or `your_<name>_here`.

**Validates: Requirements 3.3**

---

### Property 6: No Auto-Loading in Python Services

*For any* Python source file in `movie-chatbot/` or `movie-recommendation/` that is tracked by git, the file SHALL NOT contain an unconditional call to `load_dotenv()` at module scope, AND the `SettingsConfigDict` in pydantic-settings SHALL NOT have `env_file` set to a non-`None` string value.

**Validates: Requirements 3.5, 4.4**

---

### Property 7: `.env.example` Files Are Never Git-Ignored

*For any* file matching the pattern `*.env.example` in any directory of the repository, running `git check-ignore` on that file SHALL return no match — the file SHALL remain trackable and committable.

**Validates: Requirements 7.2**

---

### Property 8: No Real `.env` Files Are Git-Tracked

*For any* file matching `.env`, `.env.local`, `.env.production`, or `.env.prod` in any directory (excluding `.env.example`), that file SHALL NOT appear in the output of `git ls-files`. All such files must be excluded by `.gitignore` rules.

**Validates: Requirements 7.4, 7.5**

---

### Property 9: Consistent ES_HOST Across All Docker Compose Services

*For any* service in Docker Compose that connects to Elasticsearch (`movie-backend`, `movie-chatbot`, `movie-recommendation`, `initializer`, `mage`), the resolved `ES_HOST` value in that service's environment block SHALL be identical — all services must reference the same `${ES_HOST}` variable rather than hardcoding different values.

**Validates: Requirements 8.1, 8.4**

---

### Property 10: No Hardcoded Bonsai URLs in Chatbot Source

*For any* git-tracked file in `movie-chatbot/`, its content SHALL NOT contain the string `bonsaisearch.net`. Elasticsearch endpoints must come exclusively from injected environment variables.

**Validates: Requirements 8.3**

---

### Property 11: Chatbot and Recommendation Services Receive Only Required Variables

*For any* variable in the `chatbot` service's environment block in `docker-compose.yml`, that variable SHALL be in the set `{PYTHONUNBUFFERED, ES_HOST, ES_URL, GROQ_API_KEY, GROQ_MODEL, HF_TOKEN}`. No variable outside this set SHALL be present.

*For any* variable in the `recommendation` service's environment block, that variable SHALL be in the set `{DATABASE_URL, ES_HOST, ES_URL, HF_TOKEN, CHATBOT_URL, BACKEND_URL}`. No variable outside this set SHALL be present.

**Validates: Requirements 6.2, 6.3**

---

## Error Handling

### Missing Variable at Docker Compose Startup

Docker Compose natively emits a warning when a `${VAR}` reference cannot be resolved from the `.env` file or shell environment. Services depending on missing vars will either fail to start (e.g., Spring Boot cannot connect to DB) or behave incorrectly (e.g., empty API key).

**Mitigation**: Tất cả biến bắt buộc trong `docker-compose.yml` sẽ dùng cú pháp `${VAR:?error message}` thay vì `${VAR}` để enforce required vars và fail fast với thông báo rõ ràng cho các biến critical như DB credentials và API keys.

### Application Startup Without Required Env Vars

Pydantic-settings `BaseSettings` sẽ raise `ValidationError` khi một required field không có default value và không được tìm thấy trong environment. Đây là hành vi mong muốn — fail fast thay vì chạy với config thiếu.

**Không cần thay đổi code** ở đây vì pydantic-settings đã xử lý điều này.

### Frontend Build Without VITE_* Variables

Nếu `VITE_API_BASE_URL` không được truyền vào khi build, Vite sẽ thay thế các tham chiếu `import.meta.env.VITE_API_BASE_URL` bằng `undefined`. Frontend sẽ build thành công nhưng API calls sẽ fail.

**Mitigation**: Docker Compose `build.args` block đảm bảo biến được truyền trong local dev. Vercel dashboard phải có biến này được configure.

### `.dockerignore` Missing on chatbot

Nếu `.dockerignore` thiếu trên `movie-chatbot/`, `COPY . .` sẽ copy `.env` file vào image nếu nó tồn tại trong thư mục đó. Sau khi xóa per-service `.env` files (Requirement 3), rủi ro này giảm nhưng vẫn cần `.dockerignore` như defense-in-depth.

---

## Testing Strategy

### Unit Tests — Code Structure Validation

Các unit tests kiểm tra cấu trúc file sau khi thực hiện thay đổi:

1. **`.env` key uniqueness**: Parse root `.env`, assert `len(keys) == len(set(keys))`.
2. **`.env.example` completeness**: Parse cả hai file, assert `set(env_keys) <= set(example_keys)`.
3. **`.env.example` no real credentials**: Regex test mỗi value không match pattern credential.
4. **`config.py` no auto-loading**: Text search hoặc AST parse để verify absence của `load_dotenv()` calls và `env_file=".env"`.
5. **`docker-compose.yml` service variable sets**: Parse YAML, assert chatbot/recommendation environment blocks chứa đúng và chỉ đúng các vars được liệt kê.

### Property-Based Tests

PBT phù hợp cho một số properties vì chúng có tính phổ quát qua tập hợp biến/files. Thư viện được chọn: **Hypothesis** (Python), vì project đã dùng Python và không cần thêm dependency mới.

Mỗi property test chạy tối thiểu **100 iterations**.

**Test tagging format**: `# Feature: env-centralization, Property {N}: {property_text}`

**Property 1 Test — No Duplicate Keys**:
```python
# Feature: env-centralization, Property 1: No duplicate keys in root .env
@given(st.just(parse_env_file(".env")))
def test_no_duplicate_keys(env_vars):
    keys = [k for k, v in env_vars]
    assert len(keys) == len(set(keys))
```

**Property 3 Test — .env.example Completeness**:
```python
# Feature: env-centralization, Property 3: .env.example completeness
@given(st.just(parse_env_keys(".env")))
def test_example_covers_all_keys(env_keys):
    example_keys = parse_env_keys(".env.example")
    for key in env_keys:
        assert key in example_keys, f"{key} missing from .env.example"
```

**Property 6 Test — No Auto-Loading**:
```python
# Feature: env-centralization, Property 6: No auto-loading in Python services
@given(st.sampled_from(get_tracked_python_files(["movie-chatbot", "movie-recommendation"])))
def test_no_load_dotenv(filepath):
    content = Path(filepath).read_text()
    assert "load_dotenv()" not in content
    assert 'env_file=".env"' not in content
```

**Property 9 Test — Consistent ES_HOST Across Services**:
```python
# Feature: env-centralization, Property 9: Consistent ES_HOST across all DC services
@given(st.just(parse_docker_compose("docker-compose.yml")))
def test_es_host_consistent(compose_config):
    es_services = ["movie-backend", "chatbot", "recommendation", "initializer", "mage"]
    es_host_refs = []
    for svc in es_services:
        env = compose_config["services"][svc].get("environment", {})
        assert "ES_HOST" in env, f"ES_HOST missing from {svc}"
        es_host_refs.append(env["ES_HOST"])
    # All should reference the same variable, not hardcoded different values
    assert all("elasticsearch" in ref or "${ES_HOST}" in ref for ref in es_host_refs)
```

### Integration Tests

Các integration tests xác minh hành vi end-to-end:

1. **Docker Compose variable resolution**: `docker-compose config --quiet` không emit warnings về unresolved variables.
2. **Container environment inspection**: After `docker-compose up`, `docker inspect` trên mỗi ES-connected container show identical `ES_HOST`.
3. **Production Dockerfile verification**: Build mỗi Dockerfile trong CI và verify không có `.env` file trong image (`docker run --rm <image> ls -la | grep .env` returns empty).

### Smoke Tests

Kiểm tra setup/cấu trúc một lần:

1. **File existence**: Verify root `.env.example` tồn tại và mỗi service có `.env.example`.
2. **No service `.env` files**: Verify không có `.env`/`.env.local`/`.env.production` trong service subdirectories.
3. **`.gitignore` patterns**: Verify required patterns present trong `.gitignore`.
4. **No `.env` files tracked**: `git ls-files | grep -E '\.env$|\.env\.local$|\.env\.production$'` returns empty.
5. **No VITE_* in backend**: Verify `VITE_API_BASE_URL` absent từ `movie-backend` service trong `docker-compose.yml`.
6. **No bonsai URLs in chatbot code**: `git grep bonsaisearch.net -- movie-chatbot/` returns empty.
