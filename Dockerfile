# Use a Python slim base image
FROM python:3.11.10-slim

# Set environment variables for Python and Node.js
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_VERSION=20.18.0 \
    DJANGO_SETTINGS_MODULE=stream.settings \
    NODE_ENV=production

# Install system dependencies
# Include procps to enable pkill and other process management tools
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    procps \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app


# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependencies and install
COPY package.json ./ 
RUN npm install

# Copy the application source code
COPY . ./

# Build Tailwind CSS (ensure input.css exists)
RUN mkdir -p static/css && echo "@tailwind base;\n@tailwind components;\n@tailwind utilities;" > static/css/input.css
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css

# Expose the port
EXPOSE 8080


# Command to start the application
CMD ["./start.sh"]

