#!/bin/bash
echo "Installing Playwright browsers..."
python -m playwright install chromium
echo "Starting bot..."
python main.py
