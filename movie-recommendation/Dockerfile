FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; \
    print('Downloading model...'); \
    model = SentenceTransformer('all-MiniLM-L6-v2'); \
    print('Model cached successfully!')"

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./app ./app
COPY ./main.py .

RUN echo "# Environment variables from HF Spaces Secrets" > .env

# RUN useradd -m -u 1000 appuser && \
#     chown -R appuser:appuser /app && \
#     mkdir -p /home/appuser/.cache && \
#     cp -r /root/.cache/torch /home/appuser/.cache/ && \
#     cp -r /root/.cache/huggingface /home/appuser/.cache/ && \
#     chown -R appuser:appuser /home/appuser/.cache

# USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
