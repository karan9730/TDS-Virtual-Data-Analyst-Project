# Use Python 3.11 slim image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (Playwright & general build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    git \
    build-essential \
    wget \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libx11-xcb1 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxi6 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app
COPY . .

# Ensure uploads/ and outputs/ directories exist
RUN mkdir -p uploads outputs

# Install dependencies from your /// script manually
RUN uv pip install --system flask flask-cors werkzeug httpx google-generativeai asyncio typing beautifulsoup4 pandas playwright PyMuPDF

# Install Playwright browsers
RUN playwright install --with-deps chromium

EXPOSE 7860
CMD ["uv", "run", "app.py"]