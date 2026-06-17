# ==========================================
# STAGE 1: Builder (Tập trung cài đặt & Tải nặng)
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /app

# Chỉ cài build-essential nếu thực sự cần thiết, dọn dẹp ngay trong 1 layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Tạo môi trường ảo độc lập
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# [BÍ KÍP 1] Tách biệt nâng cấp pip để cache tốt hơn
RUN pip install --no-cache-dir --upgrade pip

# [BÍ KÍP 2] Sử dụng BuildKit Cache Mount cho pip để build siêu nhanh
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cấu hình cache model cố định
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/model_cache

# [BÍ KÍP 3] Tải model bằng đoạn script ngắn gọn, tận dụng cache layer
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/model_cache')"


# ==========================================
# STAGE 2: Final (Chỉ chứa những gì cần để CHẠY)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Chỉ cài curl, bỏ qua các gói tài liệu thừa (--no-install-recommends)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy môi trường ảo và bộ nhớ cache model từ Stage 1
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/model_cache /app/model_cache

# Kích hoạt môi trường ảo
ENV PATH="/opt/venv/bin:$PATH"
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/model_cache
ENV PYTHONUNBUFFERED=1

# --- PHẦN THAY ĐỔI LIÊN TỤC ĐƯỢC ĐƯA XUỐNG CUỐI CÙNG ---
# Khi bạn sửa code ở app/ hoặc main.py, Docker chỉ chạy lại từ layer này trở xuống (Mất < 1 giây!)
COPY ./app ./app
COPY ./main.py .

# Phân quyền Hugging Face
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]