FROM python:3.11.9-slim

WORKDIR /app

# Install ALL system dependencies needed for Playwright and browser automation
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    fonts-dejavu-core \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libgbm1 \
    libglib2.0-0 \
    libgomp1 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers AND system dependencies
RUN python -m playwright install chromium && \
    python -m playwright install-deps chromium

# Copy app
COPY . .

# Force unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Run with explicit unbuffered flag
CMD ["python", "-u", "main.py"]
