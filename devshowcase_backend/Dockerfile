# ── Backend Dockerfile ──────────────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2-binary and cryptography)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (includes gunicorn, whitenoise, dj-database-url)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source (exclude venv, db.sqlite3 via .dockerignore)
COPY . .

# Collect static files (use a dummy SECRET_KEY so this works at build time)
RUN SECRET_KEY=build-time-placeholder python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"]
