FROM python:3.11.9-slim

WORKDIR /app

# Install system dependencies needed for Playwright and browser automation
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium, firefox, webkit)
# This happens before the bot starts
RUN python -m playwright install chromium

# Copy app code
COPY . .

# Set environment to production
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
