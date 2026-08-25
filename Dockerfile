# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/apps/web
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web/ ./
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY packages/ ./packages/
COPY data/ ./data/
COPY services/ ./services/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/apps/web/dist ./apps/web/dist

# Expose port (Railway automatically sets the PORT env var)
ENV PORT=8000
EXPOSE ${PORT}

# Run the unified service
CMD uvicorn services.assistant_api.main:app --host 0.0.0.0 --port ${PORT}
