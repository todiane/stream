FROM python:3.11-slim

WORKDIR /app

# Install Node.js and required packages
RUN apt-get update && apt-get install -y \
  nodejs \
  npm \
  && rm -rf /var/lib/apt/lists/*

# Install yarn
RUN npm install -g yarn

# Set build environment
ENV PYTHONUNBUFFERED=1 \
  PORT=8080 \
  DJANGO_SETTINGS_MODULE=stream.settings \
  CLOUDINARY_CLOUD_NAME=dehgeciaw \
  CLOUDINARY_API_KEY=your_api_key \
  CLOUDINARY_API_SECRET=your_api_secret

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Install Node dependencies and build CSS
RUN yarn install
RUN yarn build:tailwind

# Collect static files (will use local storage during build)
RUN python manage.py collectstatic --noinput --verbosity 2

# Run Django
CMD python manage.py migrate && \
  python manage.py runserver 0.0.0.0:$PORT