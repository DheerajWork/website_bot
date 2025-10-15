# Base image
FROM python:3.10-slim

# Install Chromium + ChromeDriver + dependencies
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    fonts-liberation \
    libnss3 \
    libgconf-2-4 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for Selenium
ENV CHROME_BIN="/usr/bin/chromium-browser"
ENV CHROME_DRIVER="/usr/bin/chromedriver"

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
