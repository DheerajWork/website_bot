# Use Selenium Chrome standalone image as base
FROM selenium/standalone-chrome:115.0

USER root

WORKDIR /app
COPY . .

RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

ENV CHROME_BIN="/usr/bin/google-chrome"
ENV CHROME_DRIVER="/usr/bin/chromedriver"

EXPOSE 10000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
