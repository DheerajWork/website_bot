# Use Selenium Chrome standalone image as base
FROM selenium/standalone-chrome:115.0

# Set working directory
WORKDIR /app
COPY . .

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Environment variables
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV CHROME_DRIVER="/usr/bin/chromedriver"

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
