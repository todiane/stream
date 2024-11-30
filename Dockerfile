FROM python:3.11-slim

WORKDIR /app

# Install Node.js and npm
RUN apt-get update && \
  apt-get install -y --no-install-recommends nodejs npm && \
  rm -rf /var/lib/apt/lists/*

# Set build environment
ENV PYTHONUNBUFFERED=1 \
  PORT=8080

# Copy package files and install dependencies
COPY package.json .
RUN npm install

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Build Tailwind CSS
RUN npm run build:tailwind

# Run Django
CMD python manage.py migrate && \
  python manage.py runserver 0.0.0.0:$PORT
