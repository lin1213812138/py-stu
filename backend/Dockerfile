# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv sync --no-dev --frozen

COPY . .
RUN uv build --wheel --out-dir /dist

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /dist/*.whl /tmp/
RUN pip install /tmp/*.whl --no-cache-dir && \
    rm -f /tmp/*.whl && \
    groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
