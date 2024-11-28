# Use Python base image
FROM python:3.11.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_VERSION=20.18.0 \
    DJANGO_SETTINGS_MODULE=stream.settings \
    DEBUG=False \
    USE_CLOUDINARY=True \
    NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy package files and install Tailwind globally
COPY package.json .
COPY tailwind.config.js .
RUN npm install -g tailwindcss@latest postcss@latest autoprefixer@latest
RUN npm install

# Copy the project files
COPY . .

# Create directories and verify input.css exists
RUN mkdir -p static/css
RUN ls -la static/css/input.css

# Build Tailwind CSS (using globally installed tailwindcss)
RUN tailwindcss -i ./static/css/input.css -o ./static/css/output.css

# Collect static files
RUN python manage.py collectstatic --noinput

# Command to run the application
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn stream.wsgi:application --bind 0.0.0.0:$PORT"]
