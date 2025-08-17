# Use Python 3.11 slim image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv

# Install system dependencies (Playwright & build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip git build-essential wget \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 \
    libcairo2 libx11-xcb1 libx11-6 libxcb1 libxext6 libxi6 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install uv CLI
RUN pip install --no-cache-dir uv

WORKDIR /app
COPY . .

# Redirect uploads/ and outputs/ to /tmp
RUN mkdir -p /tmp/uploads/questions /tmp/outputs && \
    chmod -R 777 /tmp/uploads /tmp/outputs && \
    rm -rf uploads outputs && \
    ln -s /tmp/uploads uploads && \
    ln -s /tmp/outputs outputs

# Explicitly install Python packages for the base Python interpreter
RUN python -m pip install --no-cache-dir \
    flask flask-cors werkzeug httpx google-generativeai asyncio typing \
    beautifulsoup4 pandas numpy scipy scikit-learn matplotlib seaborn pillow \
    requests tqdm pytest fastapi openpyxl lxml pyyaml PyMuPDF playwright

# Install Playwright browsers
RUN playwright install chromium

EXPOSE 7860
CMD ["uv", "run", "app.py"]