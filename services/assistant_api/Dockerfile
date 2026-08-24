FROM python:3.11-slim

WORKDIR /app

# We assume you will add a requirements.txt in this folder or copy from root
# If you don't have one, please generate it using: pip freeze > requirements.txt
COPY requirements.txt* ./
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy the application files
COPY . .

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Start the application using uvicorn or python
# You may need to change "main:app" based on your entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
