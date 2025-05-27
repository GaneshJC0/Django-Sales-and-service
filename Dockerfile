# Use the official Python image as the base image
FROM python:3.11-slim

# Set environment variables to improve Python behavior in Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies for psycopg2 and others
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc curl \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment file dynamically created in workflow
COPY .env.prod /app/.env.prod

# Copy the full Django project codebase
COPY . .

# Collect static files (for WhiteNoise or S3 if configured)
RUN python manage.py collectstatic --noinput

# Expose Django port
EXPOSE 8000

# Start with Gunicorn for production
CMD ["gunicorn", "ecommerce.wsgi:application", "-w", "4", "-b", "0.0.0.0:8000"]
