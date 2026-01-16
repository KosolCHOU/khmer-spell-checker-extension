FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port (Cloud Run will set PORT env var)
ENV PORT=8080

# Run the application
CMD uvicorn backend_api:app --host 0.0.0.0 --port $PORT
