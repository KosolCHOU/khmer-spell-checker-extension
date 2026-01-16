FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System deps (kept minimal but functional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements (prefer CPU requirements to avoid heavy deps)
COPY requirements-cpu.txt /app/requirements-cpu.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-cpu.txt --no-cache-dir && \
    apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Collect static files (uses default settings and sqlite)
RUN python manage.py collectstatic --noinput || true

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fs http://localhost:8000/ || exit 1

# Gunicorn tuned for low memory (single worker, threads). Added --preload for startup efficiency.
CMD ["gunicorn", "keyez_site.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--max-requests", "500", "--max-requests-jitter", "50", "--timeout", "120", "--preload"]
