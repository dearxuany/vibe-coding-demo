FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask prometheus-client

# Copy application code
COPY app.py .

# Expose default port
EXPOSE 5000

ENV PORT=5000

CMD ["python", "app.py"]
