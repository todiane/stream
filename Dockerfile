FROM python:3.11-slim

WORKDIR /app

# Set build environment
ENV PYTHONUNBUFFERED=1 \
  PORT=8080

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files (including pre-built CSS)
COPY . .

# Run Django
CMD python manage.py migrate && \
  python manage.py runserver 0.0.0.0:$PORT
