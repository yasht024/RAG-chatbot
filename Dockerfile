# Build the Python backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY packages/ ./packages/
COPY data/ ./data/
COPY services/ ./services/

# Expose port (Railway automatically sets the PORT env var)
ENV PORT=8000
EXPOSE ${PORT}

# Run the backend service
CMD uvicorn services.assistant_api.main:app --host 0.0.0.0 --port ${PORT}
