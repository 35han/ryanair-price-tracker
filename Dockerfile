FROM python:3.11.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers during build
RUN python -m playwright install chromium

# Copy app
COPY . .

# Force unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Run with explicit unbuffered flag
CMD ["python", "-u", "main.py"]
