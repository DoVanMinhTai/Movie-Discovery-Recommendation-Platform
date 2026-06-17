# syntax=docker/dockerfile:1.4
# Python slim để tối ưu dung lượng image nhưng vẫn đủ thư viện nền
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Không cần build-essential/gcc: psycopg2-binary, pandas, numpy,
# scikit-learn, torch... đều có sẵn wheel nhị phân (manylinux) nên pip
# chỉ tải về, không phải compile từ source.

# Copy requirements trước để tận dụng Docker Layer Caching
COPY requirements.txt .

# QUAN TRỌNG: cài torch bản CPU-only từ index riêng của PyTorch TRƯỚC.
# sentence-transformers 3.x KHÔNG còn phụ thuộc torchvision, nên chỉ cần
# torch CPU là đủ. Bản torch mặc định trên PyPI kéo theo toàn bộ CUDA
# (~1.5GB: cuDNN, nccl, cublas, triton...) mà script chỉ chạy CPU không
# dùng tới. Cài sẵn torch CPU ở đây sẽ chặn việc đó.
#
# --mount=type=cache giữ pip cache giữa các lần build nên build lại gần
# như không phải tải lại gì.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install torch==2.2.2 \
        --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Copy mã nguồn
COPY . .

# Đảm bảo script entrypoint có quyền thực thi
RUN chmod +x entrypoint.sh

# Container chạy một lần (Job): đồng bộ Postgres -> Elasticsearch (media_contents),
# sau đó build index CBF (movies_cbf) kèm embeddings cho gợi ý phim tương tự.
CMD ["sh", "entrypoint.sh"]


