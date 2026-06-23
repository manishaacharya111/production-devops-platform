FROM python:3.11-slim

WORKDIR /app

# Create non-root user — security best practice
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies first — Docker layer caching
# If requirements.txt doesn't change, this layer is cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Health check — Docker itself checks if container is healthy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Start with Gunicorn — production WSGI server, not Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]