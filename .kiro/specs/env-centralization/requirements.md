# Requirements Document

## Introduction

Hệ thống Media Recommender System hiện có nhiều file `.env` phân tán tại các thư mục con (`movie-backend`, `movie-chatbot`, `movie-recommendation`, `movie-frontend`) và tại root project (`/.env`, `/.env.prod`). Điều này dẫn đến biến trùng lặp, giá trị không nhất quán giữa các môi trường, và không có nguồn truth duy nhất khi vận hành local hay deploy lên cloud platforms (Render, Hugging Face Spaces, Vercel).

Feature này tập trung hóa toàn bộ cấu hình môi trường vào root project, tách rõ dev/prod, và đảm bảo các service không tự load file `.env` riêng khi chạy trên production platforms.

## Glossary

- **Root `.env`**: File `.env` duy nhất tại thư mục gốc của project, là nguồn truth cho môi trường local development với Docker Compose.
- **Root `.env.prod`**: File `.env.prod` tại thư mục gốc, chứa cấu hình production dùng làm tài liệu tham khảo (không được load tự động bởi application).
- **`.env.example`**: File mẫu không chứa giá trị thật, dùng để tài liệu hóa tất cả các biến cần thiết cho từng service.
- **Env_Manager**: Hệ thống quản lý biến môi trường tập trung tại root project.
- **Config_Source**: Nguồn cung cấp biến môi trường — `root .env` cho Docker Compose, platform dashboard cho production deploy.
- **Platform_Dashboard**: Giao diện inject biến môi trường của Render, Hugging Face Spaces, và Vercel.
- **Docker_Compose**: Orchestration tool đọc biến từ root `.env` và inject vào các container.
- **Local_Dev**: Môi trường phát triển chạy bằng `docker-compose up`.
- **Production**: Môi trường deploy thật trên Render (backend), HF Spaces (chatbot/recommendation), Vercel (frontend).
- **Service_Env_File**: File `.env` riêng của từng service trong thư mục con của nó.
- **Spring_Boot**: Java framework dùng cho `movie-backend`, đọc biến môi trường qua `application.properties` / biến hệ thống.
- **FastAPI**: Python framework dùng cho `movie-chatbot` và `movie-recommendation`, đọc biến qua `os.environ` hoặc thư viện `python-dotenv`.

---

## Requirements

### Requirement 1: Nguồn Truth Duy Nhất cho Cấu Hình Dev

**User Story:** As a developer, I want all local development environment variables to be defined in a single root-level `.env` file, so that I only need to update one file to change configuration across all services.

#### Acceptance Criteria

1. THE `Env_Manager` SHALL maintain exactly one `root .env` file at the project root directory containing all variables required by all services (postgres, elasticsearch, movie-backend, movie-chatbot, movie-recommendation, movie-frontend, initializer, mage).
2. WHEN a developer runs `docker-compose up`, THE `Docker_Compose` SHALL resolve all `${VAR}` interpolations and `env_file:` references exclusively from the `root .env` file, such that no `Service_Env_File` needs to exist for the stack to start successfully.
3. THE `root .env` SHALL contain distinct variable groups delimited by comment headers (e.g., `# === DATABASE ===`), covering: Database, Elasticsearch, Service Ports, Inter-service URLs (Docker network), API Keys, CORS, Frontend, Memory Limits, and Java configuration.
4. IF a variable is referenced by two or more services in `docker-compose.yml`, THEN THE `Env_Manager` SHALL define that variable exactly once in the `root .env` file with no duplicate key entries.
5. IF a required variable is absent from `root .env` at `docker-compose up` time, THEN `Docker_Compose` SHALL emit a variable-substitution warning or error, and the affected service SHALL fail to start rather than silently using an empty string.

---

### Requirement 2: Tách Biệt Cấu Hình Dev và Production

**User Story:** As a developer, I want dev and production configurations to be clearly separated, so that I never accidentally use production credentials locally or dev values in production.

#### Acceptance Criteria

1. THE `Env_Manager` SHALL maintain two separate configuration files — `root .env` for local development and `root .env.prod` for production reference — where the following 8 environment-sensitive variables SHALL have different values in each file: `DB_URL`, `DB_URL_PYTHON`, `ES_HOST`, `ES_URL`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, and `FRONTEND_PORT`.
2. THE `root .env` SHALL contain Docker-internal hostnames (e.g., `elasticsearch`, `movie-postgres`) for inter-service URLs.
3. THE `root .env.prod` SHALL contain production hostnames and credentials (e.g., Bonsai Elasticsearch URL, Supabase PostgreSQL URL) for production reference.
4. IF `ES_HOST` is defined in `root .env`, THE value SHALL be `elasticsearch` (the Docker service name) and SHALL NOT contain `bonsaisearch.net` or any external hostname.
5. IF `ES_HOST` is defined in `root .env.prod`, THE value SHALL contain the production Bonsai cluster hostname and SHALL NOT be `elasticsearch`.
6. IF `ES_URL` is defined in `root .env`, THE value SHALL use `http://` protocol with no authentication credentials embedded in the URL. IF `ES_URL` is defined in `root .env.prod`, THE value SHALL use `https://` protocol with authentication credentials in the URL.

---

### Requirement 3: Loại Bỏ File `.env` Riêng của Từng Service

**User Story:** As a developer, I want individual services to not have their own `.env` files, so that there is no risk of a service loading stale or conflicting configuration.

#### Acceptance Criteria

1. THE `Env_Manager` SHALL ensure no file named `.env`, `.env.production`, or `.env.local` exists in `movie-backend/`, `movie-chatbot/`, `movie-recommendation/`, or `movie-frontend/` subdirectories.
2. THE `Env_Manager` SHALL provide a `.env.example` file in each of the four service subdirectories listed in criterion 1, replacing any previously existing `Service_Env_File` in those locations.
3. THE `.env.example` in each service subdirectory SHALL list every variable that service reads at runtime, with each variable assigned a sentinel placeholder value in the format `<YOUR_VALUE_HERE>` and accompanied by an inline comment explaining its purpose.
4. THE `movie-backend` Spring Boot application SHALL read environment variables from the system environment (injected by Docker Compose or Platform_Dashboard), not from any file in its directory. IF `application.properties` or any Spring config file references a local `.env` file via a `spring.config.import` directive, THEN that directive SHALL be removed.
5. THE `movie-chatbot` and `movie-recommendation` FastAPI applications SHALL NOT auto-load any `.env` file. IF either application uses `pydantic-settings` with a `SettingsConfigDict(env_file=".env")` declaration, THEN that `env_file` field SHALL be removed or set to `None`. IF either application calls `load_dotenv()` unconditionally, THEN that call SHALL be removed.

---

### Requirement 4: Không Tự Load `.env` trên Production

**User Story:** As a developer, I want production deployments to only use environment variables injected by the platform dashboard, so that no dev `.env` file is accidentally loaded by the application at runtime.

#### Acceptance Criteria

1. THE `movie-backend` application, when running on Render, SHALL source all configuration exclusively from system environment variables injected by the Render dashboard; no `.env` or `.env.production` file SHALL be present in the deployed container.
2. THE `movie-chatbot` and `movie-recommendation` applications, when running on Hugging Face Spaces, SHALL source all configuration exclusively from HF Secrets injected as environment variables; no `.env` file SHALL be present in the deployed container.
3. THE `movie-frontend` application, when built and deployed on Vercel, SHALL source all `VITE_*` variables exclusively from Vercel dashboard environment variables set at build time.
4. IF `movie-chatbot` or `movie-recommendation` contains an unconditional `load_dotenv()` call or a `pydantic-settings` `SettingsConfigDict(env_file=".env")` declaration, THEN that auto-load mechanism SHALL be removed so that no `.env` file is loaded automatically in any environment.
5. THE `movie-backend` `Dockerfile` SHALL NOT contain any `COPY` instruction that copies a file matching `*.env*` into the image.
6. THE `movie-chatbot` and `movie-recommendation` `Dockerfiles` SHALL NOT contain any `COPY` instruction that copies a file matching `.env*` into the image. IF either Dockerfile uses `COPY . .`, THEN a `.dockerignore` file in that service's directory SHALL list `.env` and `.env.*` to prevent copying any env file.

---

### Requirement 5: `.env.example` làm Tài Liệu và Onboarding

**User Story:** As a new developer, I want a comprehensive `.env.example` file at the root level, so that I can quickly understand all required variables and set up my local environment.

#### Acceptance Criteria

1. THE `Env_Manager` SHALL provide a `root .env.example` file at the project root containing every variable name present in `root .env`, each assigned a placeholder in the format `your_<variable_name>_here` (e.g., `DB_PASSWORD=your_db_password_here`), with no variable omitted.
2. THE `root .env.example` SHALL be organized into labeled sections using comment headers matching the groups in `root .env`: Database, Elasticsearch, Ports, Inter-service URLs, API Keys, CORS, Frontend, Memory Limits, Java.
3. THE `root .env.example` SHALL remain synchronized with `root .env`; IF a variable exists in `root .env` but is absent from `root .env.example`, THEN the synchronization check SHALL be considered failed.
4. THE `root .env.example` SHALL NOT contain any value that matches a real credential pattern — specifically, no value SHALL be a UUID, a base64-encoded string longer than 20 characters, an API key format (e.g., `hf_*`, `gsk_*`), a password, or an IP/hostname belonging to a production service.
5. EACH variable entry in `root .env.example` SHALL include an inline comment that states the variable's purpose and the expected value type or format (e.g., `# JDBC connection string for Spring Boot; format: jdbc:postgresql://<host>:<port>/<db>`).

---

### Requirement 6: Docker Compose Inject Đúng Biến Theo Service

**User Story:** As a developer, I want docker-compose.yml to explicitly pass only the relevant variables to each service, so that each container only receives the environment variables it actually needs.

#### Acceptance Criteria

1. THE `Docker_Compose` configuration SHALL NOT use `env_file:` for the `chatbot` or `recommendation` services; instead, each service SHALL use an explicit `environment:` block listing only the variables it requires.
2. WHEN the `chatbot` service starts in Docker Compose, THE container SHALL receive exactly `ES_HOST=http://elasticsearch:9200`, `ES_URL=http://elasticsearch:9200`, `GROQ_API_KEY`, `GROQ_MODEL`, and `HF_TOKEN` sourced from `root .env`, and SHALL NOT receive unrelated variables such as `DB_URL` or `FRONTEND_PORT`.
3. WHEN the `recommendation` service starts in Docker Compose, THE container SHALL receive `DATABASE_URL` (constructed as `postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}`), `ES_HOST`, `ES_URL`, `HF_TOKEN`, `CHATBOT_URL`, and `BACKEND_URL` sourced from `root .env`, and SHALL NOT receive frontend or Java-specific variables.
4. WHEN the `movie-backend` service starts in Docker Compose, THE container SHALL receive `DB_URL`, `DB_USER`, `DB_PASSWORD`, `ES_URL`, `ES_HOST`, `CHATBOT_URL`, `RECO_URL`, `APP_CORS_ALLOWED_ORIGINS`, and `JAVA_OPTS` from `root .env`, and SHALL NOT receive `VITE_API_BASE_URL` (a frontend build-time variable that is not consumed by Spring Boot at runtime).
5. IF a variable currently present in a service's `environment:` block is not referenced in that service's application code or Dockerfile, THEN THE `Docker_Compose` configuration SHALL remove that variable from the block.

---

### Requirement 7: `.gitignore` Bảo Vệ File Chứa Credentials Thật

**User Story:** As a developer, I want the `.gitignore` to correctly protect all real credential files while allowing example files to be committed, so that no secrets are accidentally pushed to the repository.

#### Acceptance Criteria

1. THE root `.gitignore` SHALL contain explicit entries for `.env` and `.env.prod` at the repository root (using patterns `/.env` and `/.env.prod`) to prevent committing those files.
2. THE root `.gitignore` SHALL NOT contain any rule that would cause `git check-ignore .env.example` to return a match; `.env.example` rules SHALL appear after any wildcard `.env*` rule, using a negation pattern (e.g., `!.env.example`) to ensure example files remain trackable.
3. THE root `.gitignore` SHALL contain glob patterns `**/.env`, `**/.env.local`, `**/.env.production`, and `**/.env.prod` to exclude `Service_Env_File` instances in all service subdirectories.
4. WHEN a developer clones the repository, THE only env-related files present in the working tree SHALL match the pattern `*.env.example`; no file matching `.env`, `.env.local`, `.env.production`, or `.env.prod` SHALL appear in any directory.
5. IF any `Service_Env_File` (`.env`, `.env.local`, `.env.production`) is currently tracked by git in any service subdirectory, THEN it SHALL be removed from git tracking via `git rm --cached` so that `.gitignore` rules take effect for that file.

---

### Requirement 8: ES_HOST Nhất Quán Giữa Các Service

**User Story:** As a developer, I want all services to use the same Elasticsearch endpoint in the same environment, so that there is no confusion about which cluster is being used.

#### Acceptance Criteria

1. WHEN running in Local_Dev via Docker Compose, ALL services that connect to Elasticsearch (`movie-backend`, `movie-chatbot`, `movie-recommendation`, `initializer`, `mage`) SHALL receive `ES_HOST=elasticsearch` (hostname only, no scheme or port) and `ES_URL=http://elasticsearch:9200` from `root .env`; no service SHALL receive a value containing `bonsaisearch.net` or any external hostname.
2. WHEN running in Production, ALL services that connect to Elasticsearch SHALL receive an identical `ES_HOST` value injected by the respective Platform_Dashboard, sourced from a single `ES_HOST` entry in `root .env.prod`; no service SHALL receive a different cluster URL than the others.
3. THE `movie-chatbot` service SHALL NOT have any value matching `bonsaisearch.net` hardcoded in any git-tracked file (including application code, config files, or `pydantic-settings` defaults); it SHALL rely solely on the injected `ES_HOST` environment variable.
4. WHEN all services are running simultaneously in Local_Dev, running `docker inspect <container_name>` on each Elasticsearch-connected container SHALL show identical `ES_HOST` values across all containers, confirming runtime consistency.
